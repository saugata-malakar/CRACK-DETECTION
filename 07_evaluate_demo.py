"""
Quick Demo Evaluation - 30 seconds
"""

import torch
from torch.utils.data import DataLoader, Subset
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import importlib

data_loader = importlib.import_module('02_data_loader')
model_module = importlib.import_module('03_model')

SDNET2018Dataset = data_loader.SDNET2018Dataset
get_transforms = data_loader.get_transforms
get_model = model_module.get_model


def evaluate_demo():
    print("\n" + "="*70)
    print("📊 DEMO MODEL EVALUATION")
    print("="*70)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load model
    print("\n📦 Loading demo model...")
    checkpoint = torch.load('checkpoints_demo/demo_model.pth', map_location=device)
    
    model = get_model('resnet18', num_classes=2, pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    print("✓ Model loaded")
    
    # Load test data (small subset)
    print("\n📦 Loading test data...")
    val_transform = get_transforms(augment=False)
    full_dataset = SDNET2018Dataset(root_dir='.', transform=val_transform)
    
    # Take 200 random samples for quick testing
    np.random.seed(123)
    test_indices = np.random.choice(len(full_dataset), 200, replace=False)
    test_dataset = Subset(full_dataset, test_indices)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=0)
    
    print(f"✓ Test samples: {len(test_dataset)}")
    
    # Evaluate
    print("\n🔍 Evaluating...")
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, zero_division=0)
    recall = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Accuracy:  {accuracy*100:.2f}%")
    print(f"Precision: {precision*100:.2f}%")
    print(f"Recall:    {recall*100:.2f}%")
    print(f"F1-Score:  {f1*100:.2f}%")
    print("\n⚠️  NOTE: Evaluated on 200 test samples (demo)")
    print("="*70)


if __name__ == "__main__":
    evaluate_demo()
