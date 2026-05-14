"""
Train/Validation/Test Split with Stratification
This script creates stratified splits ensuring balanced class distribution
"""

import os
import json
import shutil
from collections import defaultdict
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt


def create_stratified_splits(
    root_dir: str = '.',
    output_dir: str = 'data_splits',
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
):
    """
    Create stratified train/val/test splits
    
    Args:
        root_dir: Root directory containing Decks, Pavements, Walls folders
        output_dir: Directory to save split information
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
        seed: Random seed for reproducibility
    """
    
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"
    
    np.random.seed(seed)
    
    print("\n" + "="*70)
    print("Creating Stratified Train/Val/Test Splits")
    print("="*70)
    
    categories = ['Decks', 'Pavements', 'Walls']
    classes = ['Cracked', 'Non-cracked']
    
    # Collect all samples
    all_samples = []
    category_stats = defaultdict(lambda: defaultdict(int))
    
    for category in categories:
        for class_name in classes:
            class_dir = os.path.join(root_dir, category, class_name)
            
            if not os.path.exists(class_dir):
                print(f"Warning: {class_dir} does not exist")
                continue
            
            label = 1 if class_name == 'Cracked' else 0
            
            for img_name in os.listdir(class_dir):
                if img_name.endswith('.jpg'):
                    img_path = os.path.join(class_dir, img_name)
                    all_samples.append({
                        'path': img_path,
                        'label': label,
                        'class': class_name,
                        'category': category
                    })
                    category_stats[category][class_name] += 1
    
    print(f"\nTotal samples collected: {len(all_samples)}")
    
    # Print category statistics
    print("\nCategory breakdown:")
    for category in categories:
        total = sum(category_stats[category].values())
        cracked = category_stats[category]['Cracked']
        non_cracked = category_stats[category]['Non-cracked']
        print(f"  {category:12s}: {total:6d} total "
              f"({cracked:5d} cracked, {non_cracked:5d} non-cracked)")
    
    # Create stratification labels (category + class)
    stratify_labels = [f"{s['category']}_{s['class']}" for s in all_samples]
    
    # First split: train vs (val + test)
    train_samples, temp_samples, train_labels, temp_labels = train_test_split(
        all_samples,
        stratify_labels,
        test_size=(val_ratio + test_ratio),
        random_state=seed,
        stratify=stratify_labels
    )
    
    # Second split: val vs test
    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    val_samples, test_samples = train_test_split(
        temp_samples,
        test_size=(1 - val_ratio_adjusted),
        random_state=seed,
        stratify=temp_labels
    )
    
    # Create splits dictionary
    splits = {
        'train': train_samples,
        'val': val_samples,
        'test': test_samples
    }
    
    # Print split statistics
    print("\n" + "-"*70)
    print("Split Statistics:")
    print("-"*70)
    
    for split_name, samples in splits.items():
        total = len(samples)
        cracked = sum(1 for s in samples if s['label'] == 1)
        non_cracked = total - cracked
        
        print(f"\n{split_name.upper()} SET: {total:,} samples")
        print(f"  Cracked:     {cracked:6d} ({cracked/total*100:5.2f}%)")
        print(f"  Non-cracked: {non_cracked:6d} ({non_cracked/total*100:5.2f}%)")
        
        # Category breakdown
        for category in categories:
            cat_samples = [s for s in samples if s['category'] == category]
            cat_cracked = sum(1 for s in cat_samples if s['label'] == 1)
            cat_non_cracked = len(cat_samples) - cat_cracked
            print(f"    {category:12s}: {len(cat_samples):5d} "
                  f"({cat_cracked:4d} cracked, {cat_non_cracked:5d} non-cracked)")
    
    # Save splits to files
    os.makedirs(output_dir, exist_ok=True)
    
    for split_name, samples in splits.items():
        output_file = os.path.join(output_dir, f'{split_name}_split.json')
        
        # Save as JSON
        split_data = {
            'split': split_name,
            'total_samples': len(samples),
            'samples': [
                {
                    'path': s['path'],
                    'label': s['label'],
                    'class': s['class'],
                    'category': s['category']
                }
                for s in samples
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(split_data, f, indent=2)
        
        print(f"\n✓ Saved {split_name} split to {output_file}")
    
    # Save split summary
    summary_file = os.path.join(output_dir, 'split_summary.json')
    summary = {
        'seed': seed,
        'train_ratio': train_ratio,
        'val_ratio': val_ratio,
        'test_ratio': test_ratio,
        'total_samples': len(all_samples),
        'train_samples': len(train_samples),
        'val_samples': len(val_samples),
        'test_samples': len(test_samples),
        'categories': categories,
        'classes': classes
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Saved split summary to {summary_file}")
    
    return splits


def visualize_splits(splits: dict, output_dir: str = 'data_splits'):
    """Visualize the distribution of splits"""
    
    categories = ['Decks', 'Pavements', 'Walls']
    split_names = ['train', 'val', 'test']
    
    # Prepare data for visualization
    data = {
        'cracked': {split: [] for split in split_names},
        'non_cracked': {split: [] for split in split_names}
    }
    
    for split_name in split_names:
        samples = splits[split_name]
        
        for category in categories:
            cat_samples = [s for s in samples if s['category'] == category]
            cracked = sum(1 for s in cat_samples if s['label'] == 1)
            non_cracked = len(cat_samples) - cracked
            
            data['cracked'][split_name].append(cracked)
            data['non_cracked'][split_name].append(non_cracked)
    
    # Create visualization
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    x = np.arange(len(categories))
    width = 0.25
    
    colors = {'train': '#3498db', 'val': '#e74c3c', 'test': '#2ecc71'}
    
    for idx, split_name in enumerate(split_names):
        ax = axes[idx]
        
        cracked = data['cracked'][split_name]
        non_cracked = data['non_cracked'][split_name]
        
        bars1 = ax.bar(x - width/2, cracked, width, label='Cracked', 
                      color='#e74c3c', alpha=0.8)
        bars2 = ax.bar(x + width/2, non_cracked, width, label='Non-cracked', 
                      color='#2ecc71', alpha=0.8)
        
        ax.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Samples', fontsize=12, fontweight='bold')
        ax.set_title(f'{split_name.upper()} Set', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height):,}',
                       ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('Data Split Distribution by Category', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'split_distribution.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Split distribution visualization saved to {output_file}")
    plt.close()
    
    # Create overall split size comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart
    split_sizes = [len(splits[s]) for s in split_names]
    bars = ax1.bar(split_names, split_sizes, color=[colors[s] for s in split_names], alpha=0.8)
    ax1.set_ylabel('Number of Samples', fontsize=12, fontweight='bold')
    ax1.set_title('Split Sizes', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Pie chart
    ax2.pie(split_sizes, labels=[s.upper() for s in split_names],
           autopct='%1.1f%%', colors=[colors[s] for s in split_names],
           shadow=True, startangle=90)
    ax2.set_title('Split Proportions', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'split_sizes.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Split sizes visualization saved to {output_file}")
    plt.close()


def main():
    """Main function"""
    
    print("\n🔄 Creating stratified data splits...")
    
    # Create splits
    splits = create_stratified_splits(
        root_dir='.',
        output_dir='data_splits',
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=42
    )
    
    # Visualize splits
    print("\n📊 Generating visualizations...")
    visualize_splits(splits, output_dir='data_splits')
    
    print("\n" + "="*70)
    print("✅ Data splitting complete!")
    print("="*70)
    print("\nGenerated files in 'data_splits/' directory:")
    print("  - train_split.json")
    print("  - val_split.json")
    print("  - test_split.json")
    print("  - split_summary.json")
    print("  - split_distribution.png")
    print("  - split_sizes.png")


if __name__ == "__main__":
    main()
