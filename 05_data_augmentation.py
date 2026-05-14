"""
Data Augmentation for Crack Detection
This script demonstrates various augmentation techniques
"""

import torch
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import random
import os


class CrackAugmentation:
    """
    Custom augmentation pipeline for crack detection
    """
    
    @staticmethod
    def get_basic_augmentation():
        """Basic augmentation for training"""
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    @staticmethod
    def get_medium_augmentation():
        """Medium augmentation with rotation and color jitter"""
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    @staticmethod
    def get_heavy_augmentation():
        """Heavy augmentation with more transformations"""
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation(degrees=30),
            transforms.RandomAffine(
                degrees=0,
                translate=(0.1, 0.1),
                scale=(0.9, 1.1),
                shear=10
            ),
            transforms.ColorJitter(
                brightness=0.3,
                contrast=0.3,
                saturation=0.3,
                hue=0.1
            ),
            transforms.RandomPerspective(distortion_scale=0.2, p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    @staticmethod
    def get_test_transform():
        """No augmentation for testing"""
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])


def denormalize_image(tensor):
    """Denormalize image tensor for visualization"""
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    
    tensor = tensor * std + mean
    tensor = torch.clamp(tensor, 0, 1)
    
    return tensor


def visualize_augmentations(image_path, num_augmentations=8):
    """
    Visualize different augmentation results on a single image
    
    Args:
        image_path: Path to the image
        num_augmentations: Number of augmented versions to show
    """
    
    # Load original image
    original_img = Image.open(image_path).convert('RGB')
    
    # Define augmentation pipelines
    augmentations = {
        'Original': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor()
        ]),
        'Horizontal Flip': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomHorizontalFlip(p=1.0),
            transforms.ToTensor()
        ]),
        'Vertical Flip': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomVerticalFlip(p=1.0),
            transforms.ToTensor()
        ]),
        'Rotation 15°': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomRotation(degrees=(15, 15)),
            transforms.ToTensor()
        ]),
        'Rotation 30°': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomRotation(degrees=(30, 30)),
            transforms.ToTensor()
        ]),
        'Color Jitter': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
            transforms.ToTensor()
        ]),
        'Perspective': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomPerspective(distortion_scale=0.3, p=1.0),
            transforms.ToTensor()
        ]),
        'Affine': transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
            transforms.ToTensor()
        ])
    }
    
    # Create figure
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    for idx, (name, transform) in enumerate(augmentations.items()):
        # Apply transformation
        img_tensor = transform(original_img)
        img_np = img_tensor.permute(1, 2, 0).numpy()
        
        # Plot
        axes[idx].imshow(img_np)
        axes[idx].set_title(name, fontsize=12, fontweight='bold')
        axes[idx].axis('off')
    
    plt.suptitle('Data Augmentation Techniques', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('augmentation_examples.png', dpi=150, bbox_inches='tight')
    print("✓ Augmentation examples saved as 'augmentation_examples.png'")
    plt.close()


def compare_augmentation_levels(image_path):
    """
    Compare different augmentation intensity levels
    
    Args:
        image_path: Path to the image
    """
    
    # Load original image
    original_img = Image.open(image_path).convert('RGB')
    
    # Set seed for reproducibility
    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)
    
    # Get augmentation pipelines
    aug_levels = {
        'No Augmentation': CrackAugmentation.get_test_transform(),
        'Basic Augmentation': CrackAugmentation.get_basic_augmentation(),
        'Medium Augmentation': CrackAugmentation.get_medium_augmentation(),
        'Heavy Augmentation': CrackAugmentation.get_heavy_augmentation()
    }
    
    # Create figure
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))
    
    for row_idx, (level_name, transform) in enumerate(aug_levels.items()):
        for col_idx in range(4):
            # Apply transformation
            img_tensor = transform(original_img)
            img_denorm = denormalize_image(img_tensor)
            img_np = img_denorm.permute(1, 2, 0).numpy()
            
            # Plot
            ax = axes[row_idx, col_idx]
            ax.imshow(img_np)
            
            if col_idx == 0:
                ax.set_ylabel(level_name, fontsize=12, fontweight='bold', rotation=0, 
                            ha='right', va='center', labelpad=80)
            
            if row_idx == 0:
                ax.set_title(f'Sample {col_idx + 1}', fontsize=12, fontweight='bold')
            
            ax.axis('off')
    
    plt.suptitle('Comparison of Augmentation Intensity Levels', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('augmentation_levels.png', dpi=150, bbox_inches='tight')
    print("✓ Augmentation levels comparison saved as 'augmentation_levels.png'")
    plt.close()


def visualize_augmentation_pipeline():
    """
    Visualize augmentation pipeline on sample images from the dataset
    """
    
    print("\n" + "="*70)
    print("Data Augmentation Visualization")
    print("="*70)
    
    # Find sample images
    categories = ['Decks', 'Pavements', 'Walls']
    sample_images = []
    
    for category in categories:
        cracked_dir = os.path.join(category, 'Cracked')
        if os.path.exists(cracked_dir):
            images = [f for f in os.listdir(cracked_dir) if f.endswith('.jpg')]
            if images:
                sample_path = os.path.join(cracked_dir, images[0])
                sample_images.append((category, sample_path))
                break
    
    if not sample_images:
        print("Error: No sample images found")
        return
    
    category, image_path = sample_images[0]
    print(f"\nUsing sample image from {category}: {os.path.basename(image_path)}")
    
    # Visualize different augmentation techniques
    print("\n📊 Generating augmentation technique examples...")
    visualize_augmentations(image_path)
    
    # Compare augmentation levels
    print("📊 Generating augmentation level comparison...")
    compare_augmentation_levels(image_path)
    
    print("\n" + "="*70)
    print("✅ Augmentation visualization complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  - augmentation_examples.png")
    print("  - augmentation_levels.png")


def print_augmentation_summary():
    """Print summary of available augmentation strategies"""
    
    print("\n" + "="*70)
    print("Available Augmentation Strategies")
    print("="*70)
    
    strategies = {
        'Basic': [
            'Horizontal Flip (p=0.5)',
            'Vertical Flip (p=0.5)',
            'Normalization'
        ],
        'Medium': [
            'Horizontal Flip (p=0.5)',
            'Vertical Flip (p=0.5)',
            'Random Rotation (±15°)',
            'Color Jitter (brightness, contrast, saturation)',
            'Normalization'
        ],
        'Heavy': [
            'Horizontal Flip (p=0.5)',
            'Vertical Flip (p=0.5)',
            'Random Rotation (±30°)',
            'Random Affine (translate, scale, shear)',
            'Color Jitter (brightness, contrast, saturation, hue)',
            'Random Perspective',
            'Normalization'
        ]
    }
    
    for level, transforms_list in strategies.items():
        print(f"\n{level} Augmentation:")
        for transform in transforms_list:
            print(f"  • {transform}")
    
    print("\n" + "="*70)


def main():
    """Main function"""
    
    print("\n🎨 Starting Data Augmentation Analysis...")
    
    # Print augmentation summary
    print_augmentation_summary()
    
    # Visualize augmentations
    visualize_augmentation_pipeline()


if __name__ == "__main__":
    main()
