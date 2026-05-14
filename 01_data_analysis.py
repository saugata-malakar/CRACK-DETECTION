"""
SDNET2018 Dataset Analysis and Visualization
This script analyzes the dataset structure and visualizes sample images
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from collections import defaultdict
import random

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def analyze_dataset_structure(base_path='.'):
    """Analyze the dataset structure and count images"""
    
    categories = ['Decks', 'Pavements', 'Walls']
    classes = ['Cracked', 'Non-cracked']
    
    dataset_info = defaultdict(dict)
    
    print("=" * 60)
    print("SDNET2018 Dataset Analysis")
    print("=" * 60)
    
    total_images = 0
    
    for category in categories:
        print(f"\n{category}:")
        print("-" * 40)
        category_total = 0
        
        for class_name in classes:
            path = os.path.join(base_path, category, class_name)
            
            if os.path.exists(path):
                images = [f for f in os.listdir(path) if f.endswith('.jpg')]
                count = len(images)
                dataset_info[category][class_name] = {
                    'count': count,
                    'path': path,
                    'images': images
                }
                
                print(f"  {class_name:15s}: {count:6d} images")
                category_total += count
                total_images += count
            else:
                print(f"  {class_name:15s}: Path not found")
                dataset_info[category][class_name] = {
                    'count': 0,
                    'path': path,
                    'images': []
                }
        
        print(f"  {'Total':15s}: {category_total:6d} images")
    
    print("\n" + "=" * 60)
    print(f"TOTAL DATASET SIZE: {total_images:,} images")
    print("=" * 60)
    
    return dataset_info


def visualize_samples(dataset_info, samples_per_class=3):
    """Visualize sample images from each category and class"""
    
    categories = ['Decks', 'Pavements', 'Walls']
    classes = ['Cracked', 'Non-cracked']
    
    fig, axes = plt.subplots(len(categories), len(classes) * samples_per_class, 
                             figsize=(15, 9))
    
    fig.suptitle('SDNET2018 Dataset Sample Images', fontsize=16, fontweight='bold')
    
    for cat_idx, category in enumerate(categories):
        for class_idx, class_name in enumerate(classes):
            info = dataset_info[category][class_name]
            
            if info['count'] > 0:
                # Randomly select sample images
                sample_images = random.sample(info['images'], 
                                            min(samples_per_class, info['count']))
                
                for sample_idx, img_name in enumerate(sample_images):
                    img_path = os.path.join(info['path'], img_name)
                    img = Image.open(img_path)
                    
                    col_idx = class_idx * samples_per_class + sample_idx
                    ax = axes[cat_idx, col_idx]
                    
                    ax.imshow(img, cmap='gray')
                    ax.axis('off')
                    
                    # Add title only for the first row
                    if cat_idx == 0:
                        if sample_idx == samples_per_class // 2:
                            ax.set_title(class_name, fontsize=12, fontweight='bold')
                    
                    # Add category label on the left
                    if col_idx == 0:
                        ax.text(-0.1, 0.5, category, 
                               transform=ax.transAxes,
                               fontsize=12, fontweight='bold',
                               rotation=90, va='center', ha='right')
    
    plt.tight_layout()
    plt.savefig('dataset_samples.png', dpi=150, bbox_inches='tight')
    print("\n✓ Sample visualization saved as 'dataset_samples.png'")
    plt.close()


def plot_class_distribution(dataset_info):
    """Plot the distribution of cracked vs non-cracked images"""
    
    categories = ['Decks', 'Pavements', 'Walls']
    classes = ['Cracked', 'Non-cracked']
    
    # Prepare data for plotting
    cracked_counts = []
    non_cracked_counts = []
    
    for category in categories:
        cracked_counts.append(dataset_info[category]['Cracked']['count'])
        non_cracked_counts.append(dataset_info[category]['Non-cracked']['count'])
    
    # Create bar plot
    x = np.arange(len(categories))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Grouped bar chart
    bars1 = ax1.bar(x - width/2, cracked_counts, width, label='Cracked', 
                    color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, non_cracked_counts, width, label='Non-cracked', 
                    color='#2ecc71', alpha=0.8)
    
    ax1.set_xlabel('Category', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Images', fontsize=12, fontweight='bold')
    ax1.set_title('Class Distribution by Category', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=9)
    
    # Pie chart for overall distribution
    total_cracked = sum(cracked_counts)
    total_non_cracked = sum(non_cracked_counts)
    
    colors = ['#e74c3c', '#2ecc71']
    explode = (0.05, 0)
    
    ax2.pie([total_cracked, total_non_cracked], 
            labels=['Cracked', 'Non-cracked'],
            autopct='%1.1f%%',
            colors=colors,
            explode=explode,
            shadow=True,
            startangle=90)
    ax2.set_title('Overall Class Distribution', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('class_distribution.png', dpi=150, bbox_inches='tight')
    print("✓ Class distribution plot saved as 'class_distribution.png'")
    plt.close()


def analyze_image_properties(dataset_info, num_samples=100):
    """Analyze image properties like size, aspect ratio, etc."""
    
    print("\n" + "=" * 60)
    print("Image Properties Analysis")
    print("=" * 60)
    
    categories = ['Decks', 'Pavements', 'Walls']
    
    all_sizes = []
    all_file_sizes = []
    
    for category in categories:
        for class_name in ['Cracked', 'Non-cracked']:
            info = dataset_info[category][class_name]
            
            if info['count'] > 0:
                # Sample random images
                sample_images = random.sample(info['images'], 
                                            min(num_samples, info['count']))
                
                for img_name in sample_images:
                    img_path = os.path.join(info['path'], img_name)
                    
                    # Get image dimensions
                    img = Image.open(img_path)
                    all_sizes.append(img.size)
                    
                    # Get file size
                    file_size = os.path.getsize(img_path) / 1024  # KB
                    all_file_sizes.append(file_size)
    
    # Analyze dimensions
    widths = [s[0] for s in all_sizes]
    heights = [s[1] for s in all_sizes]
    
    print(f"\nImage Dimensions (sampled {len(all_sizes)} images):")
    print(f"  Width:  {min(widths)} x {max(widths)} px (avg: {np.mean(widths):.1f})")
    print(f"  Height: {min(heights)} x {max(heights)} px (avg: {np.mean(heights):.1f})")
    
    print(f"\nFile Size:")
    print(f"  Min:  {min(all_file_sizes):.2f} KB")
    print(f"  Max:  {max(all_file_sizes):.2f} KB")
    print(f"  Avg:  {np.mean(all_file_sizes):.2f} KB")
    print(f"  Total (estimated): {sum(all_file_sizes) * (56000 / len(all_sizes)) / 1024:.2f} MB")
    
    print("=" * 60)


def main():
    """Main function to run all analyses"""
    
    print("\n🔍 Starting SDNET2018 Dataset Analysis...\n")
    
    # Analyze dataset structure
    dataset_info = analyze_dataset_structure()
    
    # Analyze image properties
    analyze_image_properties(dataset_info)
    
    # Visualize samples
    print("\n📊 Generating visualizations...")
    visualize_samples(dataset_info, samples_per_class=3)
    plot_class_distribution(dataset_info)
    
    print("\n✅ Analysis complete!")
    print("\nGenerated files:")
    print("  - dataset_samples.png")
    print("  - class_distribution.png")


if __name__ == "__main__":
    main()
