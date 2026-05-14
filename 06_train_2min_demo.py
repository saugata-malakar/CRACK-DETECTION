"""
ULTRA-FAST 2-MINUTE DEMO TRAINING
Trains on a small subset for quick demonstration
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import json

import importlib
data_loader = importlib.import_module('02_data_loader')
model_module = importlib.import_module('03_model')

SDNET2018Dataset = data_loader.SDNET2018Dataset
get_transforms = data_loader.get_transforms
get_model = model_module.get_model


def train_fast_demo():
    """Ultra-fast training demo - completes in ~2 minutes"""
    
    print("\n" + "="*70)
    print("🚀 ULTRA-FAST 2-MINUTE DEMO")
    print("="*70)
    print("\nThis demo trains on a SMALL SUBSET for quick demonstration.")
    print("For full training, use: python 06_train.py\n")
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    # Create datasets with small subset
    print("\n📦 Loading small data subset...")
    
    train_transform = get_transforms(augment=True)
    val_transform = get_transforms(augment=False)
    
    # Full dataset
    full_dataset = SDNET2018Dataset(root_dir='.', transform=None)
    
    # Take only 1000 samples for ultra-fast training
    np.random.seed(42)
    indices = np.random.choice(len(full_dataset), 1000, replace=False)
    
    # Split: 700 train, 300 val
    train_indices = indices[:700]
    val_indices = indices[700:]
    
    train_dataset = Subset(full_dataset, train_indices)
    val_dataset = Subset(full_dataset, val_indices)
    
    # Apply transforms
    train_dataset.dataset.transform = train_transform
    val_dataset.dataset.transform = val_transform
    
    # Data loaders with larger batch size for speed
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=0)
    
    print(f"✓ Train samples: {len(train_dataset)}")
    print(f"✓ Val samples: {len(val_dataset)}")
    print(f"✓ Train batches: {len(train_loader)}")
    print(f"✓ Val batches: {len(val_loader)}")
    
    # Create lightweight model
    print("\n🤖 Creating model...")
    model = get_model('resnet18', num_classes=2, pretrained=True)
    model = model.to(device)
    print("✓ Model: ResNet-18 (pretrained)")
    
    # Training setup
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Train for just 3 epochs
    num_epochs = 3
    
    print(f"\n🏋️ Training for {num_epochs} epochs...")
    print("="*70)
    
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    
    for epoch in range(1, num_epochs + 1):
        print(f"\nEpoch {epoch}/{num_epochs}")
        print("-"*70)
        
        # Training
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc='Training', leave=False)
        for inputs, labels in pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            pbar.set_postfix({'loss': f'{loss.item():.4f}', 'acc': f'{100*correct/total:.1f}%'})
        
        train_loss = running_loss / total
        train_acc = 100 * correct / total
        
        # Validation
        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            pbar = tqdm(val_loader, desc='Validation', leave=False)
            for inputs, labels in pbar:
                inputs, labels = inputs.to(device), labels.to(device)
                
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
                pbar.set_postfix({'loss': f'{loss.item():.4f}', 'acc': f'{100*correct/total:.1f}%'})
        
        val_loss = running_loss / total
        val_acc = 100 * correct / total
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
    
    # Save model
    os.makedirs('checkpoints_demo', exist_ok=True)
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'val_acc': val_accs[-1],
        'config': {
            'model_name': 'resnet18',
            'demo': True,
            'samples': 1000,
            'epochs': num_epochs
        }
    }
    torch.save(checkpoint, 'checkpoints_demo/demo_model.pth')
    print(f"\n✓ Model saved to checkpoints_demo/demo_model.pth")
    
    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    epochs = range(1, num_epochs + 1)
    
    ax1.plot(epochs, train_losses, 'b-', label='Train Loss', linewidth=2)
    ax1.plot(epochs, val_losses, 'r-', label='Val Loss', linewidth=2)
    ax1.set_xlabel('Epoch', fontweight='bold')
    ax1.set_ylabel('Loss', fontweight='bold')
    ax1.set_title('Training Loss', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(epochs, train_accs, 'b-', label='Train Acc', linewidth=2)
    ax2.plot(epochs, val_accs, 'r-', label='Val Acc', linewidth=2)
    ax2.set_xlabel('Epoch', fontweight='bold')
    ax2.set_ylabel('Accuracy (%)', fontweight='bold')
    ax2.set_title('Training Accuracy', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('demo_training_history.png', dpi=150, bbox_inches='tight')
    print("✓ Training plot saved to demo_training_history.png")
    
    # Save metrics
    metrics = {
        'final_train_acc': train_accs[-1],
        'final_val_acc': val_accs[-1],
        'final_train_loss': train_losses[-1],
        'final_val_loss': val_losses[-1],
        'epochs': num_epochs,
        'samples': 1000
    }
    
    with open('checkpoints_demo/demo_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ DEMO TRAINING COMPLETE!")
    print("="*70)
    print(f"\nFinal Results:")
    print(f"  Train Accuracy: {train_accs[-1]:.2f}%")
    print(f"  Val Accuracy:   {val_accs[-1]:.2f}%")
    print(f"\n⚠️  NOTE: This is a DEMO on 1000 samples only!")
    print("For full training on 56,092 samples, run: python 06_train.py")
    print("\nGenerated files:")
    print("  - checkpoints_demo/demo_model.pth")
    print("  - checkpoints_demo/demo_metrics.json")
    print("  - demo_training_history.png")


if __name__ == "__main__":
    train_fast_demo()
