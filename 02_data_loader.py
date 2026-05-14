"""
SDNET2018 Data Loading Pipeline
This script creates a PyTorch dataset and data loaders for the SDNET2018 dataset
"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
from typing import Tuple, Optional, List
import matplotlib.pyplot as plt


class SDNET2018Dataset(Dataset):
    """
    PyTorch Dataset for SDNET2018 concrete crack detection
    
    Args:
        root_dir: Root directory containing Decks, Pavements, Walls folders
        categories: List of categories to include ['Decks', 'Pavements', 'Walls']
        transform: Optional transform to be applied on images
        target_transform: Optional transform to be applied on labels
    """
    
    def __init__(
        self, 
        root_dir: str = '.',
        categories: Optional[List[str]] = None,
        transform: Optional[transforms.Compose] = None,
        target_transform: Optional[transforms.Compose] = None
    ):
        self.root_dir = root_dir
        self.categories = categories or ['Decks', 'Pavements', 'Walls']
        self.transform = transform
        self.target_transform = target_transform
        
        # Class mapping
        self.class_to_idx = {'Non-cracked': 0, 'Cracked': 1}
        self.idx_to_class = {0: 'Non-cracked', 1: 'Cracked'}
        
        # Load all image paths and labels
        self.samples = []
        self._load_samples()
        
        print(f"Loaded {len(self.samples)} images from categories: {self.categories}")
        self._print_statistics()
    
    def _load_samples(self):
        """Load all image paths and their labels"""
        for category in self.categories:
            for class_name in ['Cracked', 'Non-cracked']:
                class_dir = os.path.join(self.root_dir, category, class_name)
                
                if not os.path.exists(class_dir):
                    print(f"Warning: {class_dir} does not exist")
                    continue
                
                label = self.class_to_idx[class_name]
                
                for img_name in os.listdir(class_dir):
                    if img_name.endswith('.jpg'):
                        img_path = os.path.join(class_dir, img_name)
                        self.samples.append((img_path, label, category))
    
    def _print_statistics(self):
        """Print dataset statistics"""
        cracked = sum(1 for _, label, _ in self.samples if label == 1)
        non_cracked = sum(1 for _, label, _ in self.samples if label == 0)
        
        print(f"  Cracked: {cracked} ({cracked/len(self.samples)*100:.1f}%)")
        print(f"  Non-cracked: {non_cracked} ({non_cracked/len(self.samples)*100:.1f}%)")
        
        # Category breakdown
        for category in self.categories:
            cat_samples = [s for s in self.samples if s[2] == category]
            print(f"  {category}: {len(cat_samples)} images")
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label, category = self.samples[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        if self.target_transform:
            label = self.target_transform(label)
        
        return image, label
    
    def get_sample_info(self, idx: int) -> dict:
        """Get detailed information about a sample"""
        img_path, label, category = self.samples[idx]
        return {
            'path': img_path,
            'label': label,
            'class_name': self.idx_to_class[label],
            'category': category
        }


def get_transforms(augment: bool = False, img_size: int = 256) -> transforms.Compose:
    """
    Get image transforms for training or validation
    
    Args:
        augment: Whether to apply data augmentation
        img_size: Target image size
    
    Returns:
        Composed transforms
    """
    
    if augment:
        # Training transforms with augmentation
        transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    else:
        # Validation/Test transforms without augmentation
        transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    return transform


def create_data_loaders(
    root_dir: str = '.',
    batch_size: int = 32,
    train_split: float = 0.7,
    val_split: float = 0.15,
    test_split: float = 0.15,
    num_workers: int = 4,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train, validation, and test data loaders
    
    Args:
        root_dir: Root directory of the dataset
        batch_size: Batch size for data loaders
        train_split: Proportion of data for training
        val_split: Proportion of data for validation
        test_split: Proportion of data for testing
        num_workers: Number of worker processes for data loading
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    
    assert abs(train_split + val_split + test_split - 1.0) < 1e-6, \
        "Splits must sum to 1.0"
    
    # Set random seed
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Create full dataset
    print("\n" + "="*60)
    print("Creating Data Loaders")
    print("="*60)
    
    full_dataset = SDNET2018Dataset(
        root_dir=root_dir,
        transform=None  # We'll apply transforms after splitting
    )
    
    # Calculate split sizes
    total_size = len(full_dataset)
    train_size = int(train_split * total_size)
    val_size = int(val_split * total_size)
    test_size = total_size - train_size - val_size
    
    print(f"\nSplit sizes:")
    print(f"  Train: {train_size} ({train_split*100:.1f}%)")
    print(f"  Val:   {val_size} ({val_split*100:.1f}%)")
    print(f"  Test:  {test_size} ({test_split*100:.1f}%)")
    
    # Split dataset
    train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
        full_dataset, 
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    # Apply transforms
    train_transform = get_transforms(augment=True)
    val_test_transform = get_transforms(augment=False)
    
    # Wrap datasets with transforms
    train_dataset.dataset.transform = train_transform
    val_dataset.dataset.transform = val_test_transform
    test_dataset.dataset.transform = val_test_transform
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"\nData loaders created:")
    print(f"  Train batches: {len(train_loader)}")
    print(f"  Val batches:   {len(val_loader)}")
    print(f"  Test batches:  {len(test_loader)}")
    print("="*60)
    
    return train_loader, val_loader, test_loader


def visualize_batch(data_loader: DataLoader, num_images: int = 8):
    """Visualize a batch of images from the data loader"""
    
    # Get a batch
    images, labels = next(iter(data_loader))
    
    # Denormalize images for visualization
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    
    images_denorm = images * std + mean
    images_denorm = torch.clamp(images_denorm, 0, 1)
    
    # Plot
    num_images = min(num_images, len(images))
    fig, axes = plt.subplots(2, num_images // 2, figsize=(15, 6))
    axes = axes.flatten()
    
    class_names = ['Non-cracked', 'Cracked']
    
    for idx in range(num_images):
        img = images_denorm[idx].permute(1, 2, 0).numpy()
        label = labels[idx].item()
        
        axes[idx].imshow(img)
        axes[idx].set_title(f'{class_names[label]}', 
                           fontweight='bold',
                           color='red' if label == 1 else 'green')
        axes[idx].axis('off')
    
    plt.suptitle('Sample Batch from Data Loader', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('data_loader_samples.png', dpi=150, bbox_inches='tight')
    print("\n✓ Data loader samples saved as 'data_loader_samples.png'")
    plt.close()


def test_data_loader():
    """Test the data loader functionality"""
    
    print("\n🧪 Testing Data Loader...")
    
    # Create data loaders
    train_loader, val_loader, test_loader = create_data_loaders(
        batch_size=32,
        train_split=0.7,
        val_split=0.15,
        test_split=0.15,
        num_workers=0,  # Use 0 for testing to avoid multiprocessing issues
        seed=42
    )
    
    # Test loading a batch
    print("\n📦 Loading a test batch...")
    images, labels = next(iter(train_loader))
    print(f"  Batch shape: {images.shape}")
    print(f"  Labels shape: {labels.shape}")
    print(f"  Image dtype: {images.dtype}")
    print(f"  Image range: [{images.min():.3f}, {images.max():.3f}]")
    
    # Visualize batch
    print("\n📊 Visualizing batch...")
    visualize_batch(train_loader, num_images=8)
    
    print("\n✅ Data loader test complete!")
    
    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    test_data_loader()
