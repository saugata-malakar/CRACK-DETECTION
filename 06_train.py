"""
Complete Training Script for Concrete Crack Detection
This script trains a CNN model for crack detection with full monitoring
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import time
import json
import os
from datetime import datetime

# Import custom modules
import importlib
data_loader = importlib.import_module('02_data_loader')
model_module = importlib.import_module('03_model')

create_data_loaders = data_loader.create_data_loaders
get_model = model_module.get_model
count_parameters = model_module.count_parameters


class EarlyStopping:
    """Early stopping to stop training when validation loss doesn't improve"""
    
    def __init__(self, patience=7, min_delta=0, verbose=True):
        self.patience = patience
        self.min_delta = min_delta
        self.verbose = verbose
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        self.best_epoch = 0
    
    def __call__(self, val_loss, epoch):
        if self.best_loss is None:
            self.best_loss = val_loss
            self.best_epoch = epoch
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.verbose:
                print(f'EarlyStopping counter: {self.counter}/{self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.best_epoch = epoch
            self.counter = 0


class MetricsTracker:
    """Track training metrics"""
    
    def __init__(self):
        self.train_losses = []
        self.val_losses = []
        self.train_accs = []
        self.val_accs = []
        self.learning_rates = []
    
    def update(self, train_loss, val_loss, train_acc, val_acc, lr):
        self.train_losses.append(train_loss)
        self.val_losses.append(val_loss)
        self.train_accs.append(train_acc)
        self.val_accs.append(val_acc)
        self.learning_rates.append(lr)
    
    def plot(self, save_path='training_history.png'):
        """Plot training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        epochs = range(1, len(self.train_losses) + 1)
        
        # Loss plot
        axes[0, 0].plot(epochs, self.train_losses, 'b-', label='Train Loss', linewidth=2)
        axes[0, 0].plot(epochs, self.val_losses, 'r-', label='Val Loss', linewidth=2)
        axes[0, 0].set_xlabel('Epoch', fontweight='bold')
        axes[0, 0].set_ylabel('Loss', fontweight='bold')
        axes[0, 0].set_title('Training and Validation Loss', fontweight='bold', fontsize=14)
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Accuracy plot
        axes[0, 1].plot(epochs, self.train_accs, 'b-', label='Train Acc', linewidth=2)
        axes[0, 1].plot(epochs, self.val_accs, 'r-', label='Val Acc', linewidth=2)
        axes[0, 1].set_xlabel('Epoch', fontweight='bold')
        axes[0, 1].set_ylabel('Accuracy (%)', fontweight='bold')
        axes[0, 1].set_title('Training and Validation Accuracy', fontweight='bold', fontsize=14)
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Learning rate plot
        axes[1, 0].plot(epochs, self.learning_rates, 'g-', linewidth=2)
        axes[1, 0].set_xlabel('Epoch', fontweight='bold')
        axes[1, 0].set_ylabel('Learning Rate', fontweight='bold')
        axes[1, 0].set_title('Learning Rate Schedule', fontweight='bold', fontsize=14)
        axes[1, 0].set_yscale('log')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Loss difference plot
        loss_diff = [abs(t - v) for t, v in zip(self.train_losses, self.val_losses)]
        axes[1, 1].plot(epochs, loss_diff, 'm-', linewidth=2)
        axes[1, 1].set_xlabel('Epoch', fontweight='bold')
        axes[1, 1].set_ylabel('|Train Loss - Val Loss|', fontweight='bold')
        axes[1, 1].set_title('Overfitting Indicator', fontweight='bold', fontsize=14)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"\n✓ Training history plot saved to {save_path}")
        plt.close()


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(dataloader, desc='Training', leave=False)
    
    for inputs, labels in pbar:
        inputs, labels = inputs.to(device), labels.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Statistics
        running_loss += loss.item() * inputs.size(0)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        # Update progress bar
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100 * correct / total:.2f}%'
        })
    
    epoch_loss = running_loss / total
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc


def validate(model, dataloader, criterion, device):
    """Validate the model"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc='Validation', leave=False)
        
        for inputs, labels in pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Statistics
            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100 * correct / total:.2f}%'
            })
    
    epoch_loss = running_loss / total
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc


def train_model(
    model_name='resnet18',
    batch_size=32,
    num_epochs=50,
    learning_rate=0.001,
    weight_decay=1e-4,
    patience=10,
    output_dir='checkpoints',
    pretrained=True,
    freeze_backbone=False
):
    """
    Complete training pipeline
    
    Args:
        model_name: Name of the model architecture
        batch_size: Batch size for training
        num_epochs: Maximum number of epochs
        learning_rate: Initial learning rate
        weight_decay: L2 regularization weight
        patience: Early stopping patience
        output_dir: Directory to save checkpoints
        pretrained: Use pretrained weights
        freeze_backbone: Freeze backbone weights
    """
    
    print("\n" + "="*70)
    print("CONCRETE CRACK DETECTION - TRAINING")
    print("="*70)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Create data loaders
    print("\n" + "-"*70)
    print("Loading Data...")
    print("-"*70)
    
    train_loader, val_loader, test_loader = create_data_loaders(
        batch_size=batch_size,
        num_workers=0  # Set to 0 for Windows compatibility
    )
    
    # Create model
    print("\n" + "-"*70)
    print("Creating Model...")
    print("-"*70)
    
    model = get_model(
        model_name=model_name,
        num_classes=2,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone
    )
    model = model.to(device)
    
    params = count_parameters(model)
    print(f"\nModel: {model_name}")
    print(f"Total parameters: {params['total']:,}")
    print(f"Trainable parameters: {params['trainable']:,}")
    if params['frozen'] > 0:
        print(f"Frozen parameters: {params['frozen']:,}")
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay
    )
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=5
    )
    
    # Early stopping
    early_stopping = EarlyStopping(patience=patience, verbose=True)
    
    # Metrics tracker
    metrics = MetricsTracker()
    
    # Training configuration
    config = {
        'model_name': model_name,
        'batch_size': batch_size,
        'num_epochs': num_epochs,
        'learning_rate': learning_rate,
        'weight_decay': weight_decay,
        'patience': patience,
        'pretrained': pretrained,
        'freeze_backbone': freeze_backbone,
        'device': str(device),
        'total_params': params['total'],
        'trainable_params': params['trainable']
    }
    
    # Save configuration
    config_path = os.path.join(output_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\n✓ Configuration saved to {config_path}")
    
    # Training loop
    print("\n" + "="*70)
    print("Starting Training...")
    print("="*70)
    
    best_val_acc = 0.0
    start_time = time.time()
    
    for epoch in range(1, num_epochs + 1):
        print(f"\nEpoch {epoch}/{num_epochs}")
        print("-" * 70)
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        # Update learning rate
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        # Update metrics
        metrics.update(train_loss, val_loss, train_acc, val_acc, current_lr)
        
        # Print epoch summary
        print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        print(f"Learning Rate: {current_lr:.6f}")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
                'config': config
            }
            checkpoint_path = os.path.join(output_dir, 'best_model.pth')
            torch.save(checkpoint, checkpoint_path)
            print(f"✓ Best model saved (Val Acc: {val_acc:.2f}%)")
        
        # Early stopping
        early_stopping(val_loss, epoch)
        if early_stopping.early_stop:
            print(f"\n⚠ Early stopping triggered at epoch {epoch}")
            print(f"Best epoch was {early_stopping.best_epoch}")
            break
    
    # Training complete
    training_time = time.time() - start_time
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print(f"Total training time: {training_time/60:.2f} minutes")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    
    # Plot training history
    metrics.plot(os.path.join(output_dir, 'training_history.png'))
    
    # Save final metrics
    final_metrics = {
        'best_val_acc': best_val_acc,
        'training_time_minutes': training_time / 60,
        'epochs_trained': epoch,
        'train_losses': metrics.train_losses,
        'val_losses': metrics.val_losses,
        'train_accs': metrics.train_accs,
        'val_accs': metrics.val_accs
    }
    
    metrics_path = os.path.join(output_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(final_metrics, f, indent=2)
    print(f"✓ Metrics saved to {metrics_path}")
    
    return model, metrics


def main():
    """Main training function"""
    
    # Training configuration
    config = {
        'model_name': 'resnet18',  # Options: simple_cnn, resnet18, resnet34, efficientnet_b0, vgg16
        'batch_size': 32,
        'num_epochs': 30,
        'learning_rate': 0.001,
        'weight_decay': 1e-4,
        'patience': 10,
        'pretrained': True,
        'freeze_backbone': False,
        'output_dir': 'checkpoints'
    }
    
    # Train model
    model, metrics = train_model(**config)
    
    print("\n✅ Training pipeline complete!")
    print(f"\nCheckpoint files saved in '{config['output_dir']}/' directory:")
    print("  - best_model.pth (model checkpoint)")
    print("  - config.json (training configuration)")
    print("  - metrics.json (training metrics)")
    print("  - training_history.png (training plots)")


if __name__ == "__main__":
    main()
