"""
Prediction Script for New Images
This script makes predictions on new concrete images
"""

import torch
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

import importlib
model_module = importlib.import_module('03_model')
get_model = model_module.get_model


class CrackPredictor:
    """Crack detection predictor"""
    
    def __init__(self, checkpoint_path, device=None):
        """
        Initialize predictor
        
        Args:
            checkpoint_path: Path to model checkpoint
            device: Device to run inference on
        """
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load checkpoint
        print(f"Loading model from {checkpoint_path}...")
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.config = checkpoint['config']
        
        # Create model
        self.model = get_model(
            model_name=self.config['model_name'],
            num_classes=2,
            pretrained=False
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Define transforms
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.class_names = ['Non-cracked', 'Cracked']
        
        print(f"✓ Model loaded successfully")
        print(f"  Model: {self.config['model_name']}")
        print(f"  Device: {self.device}")
    
    def predict_image(self, image_path):
        """
        Predict crack in a single image
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with prediction results
        """
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        predicted_class = predicted.item()
        confidence_score = confidence.item()
        
        result = {
            'image_path': image_path,
            'predicted_class': self.class_names[predicted_class],
            'predicted_label': predicted_class,
            'confidence': confidence_score,
            'probabilities': {
                'Non-cracked': probs[0][0].item(),
                'Cracked': probs[0][1].item()
            }
        }
        
        return result
    
    def predict_batch(self, image_paths):
        """
        Predict cracks in multiple images
        
        Args:
            image_paths: List of image paths
        
        Returns:
            List of prediction results
        """
        results = []
        
        for image_path in image_paths:
            result = self.predict_image(image_path)
            results.append(result)
        
        return results
    
    def predict_directory(self, directory_path, pattern='*.jpg'):
        """
        Predict cracks in all images in a directory
        
        Args:
            directory_path: Path to directory
            pattern: File pattern to match
        
        Returns:
            List of prediction results
        """
        image_paths = glob.glob(os.path.join(directory_path, pattern))
        
        if not image_paths:
            print(f"No images found in {directory_path} with pattern {pattern}")
            return []
        
        print(f"Found {len(image_paths)} images")
        return self.predict_batch(image_paths)


def visualize_predictions(predictor, image_paths, save_path='predictions.png'):
    """
    Visualize predictions on multiple images
    
    Args:
        predictor: CrackPredictor instance
        image_paths: List of image paths
        save_path: Path to save visualization
    """
    num_images = len(image_paths)
    cols = 4
    rows = (num_images + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    for idx, image_path in enumerate(image_paths):
        # Make prediction
        result = predictor.predict_image(image_path)
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Plot
        ax = axes[idx]
        ax.imshow(image)
        
        # Set title with prediction
        predicted_class = result['predicted_class']
        confidence = result['confidence']
        
        color = 'red' if predicted_class == 'Cracked' else 'green'
        title = f"{predicted_class}\n({confidence*100:.1f}%)"
        
        ax.set_title(title, fontsize=12, fontweight='bold', color=color)
        ax.axis('off')
    
    # Hide unused subplots
    for idx in range(num_images, len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle('Crack Detection Predictions', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Predictions visualization saved to {save_path}")
    plt.close()


def visualize_prediction_details(predictor, image_path, save_path='prediction_detail.png'):
    """
    Visualize detailed prediction for a single image
    
    Args:
        predictor: CrackPredictor instance
        image_path: Path to image
        save_path: Path to save visualization
    """
    # Make prediction
    result = predictor.predict_image(image_path)
    
    # Load image
    image = Image.open(image_path).convert('RGB')
    
    # Create figure
    fig = plt.figure(figsize=(14, 6))
    
    # Plot image
    ax1 = plt.subplot(1, 2, 1)
    ax1.imshow(image)
    ax1.set_title('Input Image', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Plot prediction probabilities
    ax2 = plt.subplot(1, 2, 2)
    
    classes = ['Non-cracked', 'Cracked']
    probs = [result['probabilities']['Non-cracked'], 
             result['probabilities']['Cracked']]
    colors = ['green', 'red']
    
    bars = ax2.barh(classes, probs, color=colors, alpha=0.7)
    ax2.set_xlim([0, 1])
    ax2.set_xlabel('Probability', fontsize=12, fontweight='bold')
    ax2.set_title('Prediction Probabilities', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for bar, prob in zip(bars, probs):
        width = bar.get_width()
        ax2.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                f'{prob*100:.2f}%',
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    # Add prediction text
    predicted_class = result['predicted_class']
    confidence = result['confidence']
    
    fig.text(0.5, 0.02, 
            f"Prediction: {predicted_class} (Confidence: {confidence*100:.2f}%)",
            ha='center', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ Detailed prediction saved to {save_path}")
    plt.close()


def demo_predictions():
    """Demo predictions on sample images from the dataset"""
    
    print("\n" + "="*70)
    print("CRACK DETECTION - PREDICTION DEMO")
    print("="*70)
    
    checkpoint_path = 'checkpoints/best_model.pth'
    
    if not os.path.exists(checkpoint_path):
        print(f"\n❌ Error: Checkpoint not found at {checkpoint_path}")
        print("Please train a model first using 06_train.py")
        return
    
    # Create predictor
    predictor = CrackPredictor(checkpoint_path)
    
    # Find sample images
    print("\n📸 Finding sample images...")
    
    sample_images = []
    categories = ['Decks', 'Pavements', 'Walls']
    
    for category in categories:
        for class_name in ['Cracked', 'Non-cracked']:
            class_dir = os.path.join(category, class_name)
            if os.path.exists(class_dir):
                images = glob.glob(os.path.join(class_dir, '*.jpg'))
                if images:
                    # Take 2 samples from each category/class
                    sample_images.extend(images[:2])
    
    if not sample_images:
        print("❌ No sample images found")
        return
    
    # Limit to 12 images for visualization
    sample_images = sample_images[:12]
    
    print(f"Selected {len(sample_images)} sample images")
    
    # Make predictions
    print("\n🔍 Making predictions...")
    results = predictor.predict_batch(sample_images)
    
    # Print results
    print("\n" + "-"*70)
    print("PREDICTION RESULTS")
    print("-"*70)
    
    for result in results:
        image_name = os.path.basename(result['image_path'])
        predicted = result['predicted_class']
        confidence = result['confidence']
        
        print(f"{image_name:30s} -> {predicted:12s} ({confidence*100:.2f}%)")
    
    # Visualize predictions
    print("\n📊 Generating visualizations...")
    visualize_predictions(predictor, sample_images, 'predictions_demo.png')
    
    # Detailed visualization for first image
    if sample_images:
        visualize_prediction_details(predictor, sample_images[0], 
                                    'prediction_detail_demo.png')
    
    print("\n" + "="*70)
    print("✅ Prediction demo complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  - predictions_demo.png")
    print("  - prediction_detail_demo.png")


def main():
    """Main prediction function"""
    demo_predictions()


if __name__ == "__main__":
    main()
