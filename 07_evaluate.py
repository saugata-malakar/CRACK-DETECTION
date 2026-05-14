"""
Model Evaluation Script
This script evaluates the trained model on the test set
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, classification_report, 
    roc_curve, auc, precision_recall_curve
)
import seaborn as sns
from tqdm import tqdm
import json
import os

import importlib
data_loader = importlib.import_module('02_data_loader')
model_module = importlib.import_module('03_model')

create_data_loaders = data_loader.create_data_loaders
get_model = model_module.get_model


def evaluate_model(model, dataloader, device):
    """
    Evaluate model and collect predictions
    
    Returns:
        all_labels: Ground truth labels
        all_preds: Predicted labels
        all_probs: Prediction probabilities
    """
    model.eval()
    
    all_labels = []
    all_preds = []
    all_probs = []
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc='Evaluating')
        
        for inputs, labels in pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs, 1)
            
            # Collect results
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(predicted.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    return np.array(all_labels), np.array(all_preds), np.array(all_probs)


def plot_confusion_matrix(y_true, y_pred, save_path='confusion_matrix.png'):
    """Plot confusion matrix"""
    
    cm = confusion_matrix(y_true, y_pred)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Non-cracked', 'Cracked'],
                yticklabels=['Non-cracked', 'Cracked'],
                cbar_kws={'label': 'Count'},
                ax=ax)
    
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    
    # Add percentages
    total = cm.sum()
    for i in range(2):
        for j in range(2):
            percentage = cm[i, j] / total * 100
            ax.text(j + 0.5, i + 0.7, f'({percentage:.1f}%)', 
                   ha='center', va='center', fontsize=10, color='gray')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ Confusion matrix saved to {save_path}")
    plt.close()
    
    return cm


def plot_roc_curve(y_true, y_probs, save_path='roc_curve.png'):
    """Plot ROC curve"""
    
    # Calculate ROC curve
    fpr, tpr, thresholds = roc_curve(y_true, y_probs[:, 1])
    roc_auc = auc(fpr, tpr)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.plot(fpr, tpr, color='darkorange', lw=2, 
           label=f'ROC curve (AUC = {roc_auc:.4f})')
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
           label='Random Classifier')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    ax.set_title('Receiver Operating Characteristic (ROC) Curve', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ ROC curve saved to {save_path}")
    plt.close()
    
    return roc_auc


def plot_precision_recall_curve(y_true, y_probs, save_path='precision_recall_curve.png'):
    """Plot Precision-Recall curve"""
    
    # Calculate PR curve
    precision, recall, thresholds = precision_recall_curve(y_true, y_probs[:, 1])
    pr_auc = auc(recall, precision)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.plot(recall, precision, color='blue', lw=2, 
           label=f'PR curve (AUC = {pr_auc:.4f})')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('Recall', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precision', fontsize=12, fontweight='bold')
    ax.set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
    ax.legend(loc='lower left', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ Precision-Recall curve saved to {save_path}")
    plt.close()
    
    return pr_auc


def calculate_metrics(y_true, y_pred, y_probs):
    """Calculate comprehensive metrics"""
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # Calculate metrics
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    # ROC AUC
    fpr, tpr, _ = roc_curve(y_true, y_probs[:, 1])
    roc_auc = auc(fpr, tpr)
    
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'specificity': specificity,
        'roc_auc': roc_auc,
        'true_positives': int(tp),
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn)
    }
    
    return metrics


def print_evaluation_report(metrics):
    """Print formatted evaluation report"""
    
    print("\n" + "="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    
    print(f"\nOverall Metrics:")
    print(f"  Accuracy:    {metrics['accuracy']*100:.2f}%")
    print(f"  Precision:   {metrics['precision']*100:.2f}%")
    print(f"  Recall:      {metrics['recall']*100:.2f}%")
    print(f"  F1-Score:    {metrics['f1_score']*100:.2f}%")
    print(f"  Specificity: {metrics['specificity']*100:.2f}%")
    print(f"  ROC AUC:     {metrics['roc_auc']:.4f}")
    
    print(f"\nConfusion Matrix Values:")
    print(f"  True Positives:  {metrics['true_positives']}")
    print(f"  True Negatives:  {metrics['true_negatives']}")
    print(f"  False Positives: {metrics['false_positives']}")
    print(f"  False Negatives: {metrics['false_negatives']}")
    
    print("="*70)


def evaluate_checkpoint(
    checkpoint_path='checkpoints/best_model.pth',
    output_dir='evaluation_results',
    batch_size=32
):
    """
    Evaluate a trained model checkpoint
    
    Args:
        checkpoint_path: Path to model checkpoint
        output_dir: Directory to save evaluation results
        batch_size: Batch size for evaluation
    """
    
    print("\n" + "="*70)
    print("MODEL EVALUATION")
    print("="*70)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    
    # Load checkpoint
    print(f"\nLoading checkpoint from {checkpoint_path}...")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = checkpoint['config']
    
    print(f"Model: {config['model_name']}")
    print(f"Training epoch: {checkpoint['epoch']}")
    print(f"Validation accuracy: {checkpoint['val_acc']:.2f}%")
    
    # Create data loaders
    print("\nLoading test data...")
    _, _, test_loader = create_data_loaders(
        batch_size=batch_size,
        num_workers=0  # Set to 0 for Windows compatibility
    )
    
    # Create model
    print("\nCreating model...")
    model = get_model(
        model_name=config['model_name'],
        num_classes=2,
        pretrained=False  # Don't need pretrained weights when loading checkpoint
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    
    # Evaluate
    print("\nEvaluating on test set...")
    y_true, y_pred, y_probs = evaluate_model(model, test_loader, device)
    
    # Calculate metrics
    metrics = calculate_metrics(y_true, y_pred, y_probs)
    
    # Print report
    print_evaluation_report(metrics)
    
    # Generate visualizations
    print("\n📊 Generating evaluation plots...")
    plot_confusion_matrix(y_true, y_pred, 
                         os.path.join(output_dir, 'confusion_matrix.png'))
    plot_roc_curve(y_true, y_probs, 
                  os.path.join(output_dir, 'roc_curve.png'))
    plot_precision_recall_curve(y_true, y_probs, 
                               os.path.join(output_dir, 'precision_recall_curve.png'))
    
    # Save metrics
    metrics_path = os.path.join(output_dir, 'test_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n✓ Metrics saved to {metrics_path}")
    
    # Save classification report
    report = classification_report(y_true, y_pred, 
                                   target_names=['Non-cracked', 'Cracked'],
                                   digits=4)
    report_path = os.path.join(output_dir, 'classification_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✓ Classification report saved to {report_path}")
    
    print("\n" + "="*70)
    print("✅ Evaluation complete!")
    print("="*70)
    print(f"\nResults saved in '{output_dir}/' directory:")
    print("  - test_metrics.json")
    print("  - classification_report.txt")
    print("  - confusion_matrix.png")
    print("  - roc_curve.png")
    print("  - precision_recall_curve.png")
    
    return metrics


def main():
    """Main evaluation function"""
    
    checkpoint_path = 'checkpoints/best_model.pth'
    
    if not os.path.exists(checkpoint_path):
        print(f"\n❌ Error: Checkpoint not found at {checkpoint_path}")
        print("Please train a model first using 06_train.py")
        return
    
    # Evaluate model
    metrics = evaluate_checkpoint(
        checkpoint_path=checkpoint_path,
        output_dir='evaluation_results',
        batch_size=32
    )


if __name__ == "__main__":
    main()
