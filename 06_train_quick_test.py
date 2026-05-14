"""
Quick Training Test - Just 2 epochs to verify everything works
"""

import importlib
import sys

# Import the training module
train_module = importlib.import_module('06_train')

# Override the config for quick testing
config = {
    'model_name': 'resnet18',
    'batch_size': 32,
    'num_epochs': 2,  # Just 2 epochs for testing
    'learning_rate': 0.001,
    'weight_decay': 1e-4,
    'patience': 10,
    'pretrained': True,
    'freeze_backbone': False,
    'output_dir': 'checkpoints'
}

print("\n" + "="*70)
print("QUICK TRAINING TEST (2 epochs only)")
print("="*70)
print("\nThis is a quick test to verify the training pipeline works.")
print("For full training, use: python 06_train.py\n")

# Train model
model, metrics = train_module.train_model(**config)

print("\n✅ Quick training test successful!")
print("The full training pipeline is working correctly.")
print("\nTo train a full model, run: python 06_train.py")
