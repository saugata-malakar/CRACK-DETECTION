"""
Quick Demo Predictions - 20 seconds
"""

import torch
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import os
import glob
import importlib

model_module = importlib.import_module('03_model')
get_model = model_module.get_model


def predict_demo():
    print("\n" + "="*70)
    print("🔮 DEMO PREDICTIONS")
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
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Find sample images
    print("\n📸 Finding sample images...")
    sample_images = []
    
    for category in ['Decks', 'Pavements', 'Walls']:
        for class_name in ['Cracked', 'Non-cracked']:
            class_dir = os.path.join(category, class_name)
            if os.path.exists(class_dir):
                images = glob.glob(os.path.join(class_dir, '*.jpg'))
                if images:
                    sample_images.append(images[0])
                    if len(sample_images) >= 6:
                        break
        if len(sample_images) >= 6:
            break
    
    print(f"✓ Found {len(sample_images)} sample images")
    
    # Make predictions
    print("\n🔍 Making predictions...")
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    
    class_names = ['Non-cracked', 'Cracked']
    
    for idx, img_path in enumerate(sample_images):
        # Load and predict
        image = Image.open(img_path).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        predicted_class = class_names[predicted.item()]
        confidence_score = confidence.item()
        
        # Plot
        axes[idx].imshow(image)
        color = 'red' if predicted_class == 'Cracked' else 'green'
        axes[idx].set_title(f'{predicted_class}\n({confidence_score*100:.1f}%)', 
                           fontweight='bold', color=color, fontsize=11)
        axes[idx].axis('off')
    
    plt.suptitle('Demo Model Predictions', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('demo_predictions.png', dpi=150, bbox_inches='tight')
    print("✓ Predictions saved to demo_predictions.png")
    
    print("\n" + "="*70)
    print("✅ DEMO PREDICTIONS COMPLETE!")
    print("="*70)
    print("\nGenerated: demo_predictions.png")
    print("\n⚠️  NOTE: This is a demo model trained on 1000 samples")
    print("For production use, train on full dataset with: python 06_train.py")


if __name__ == "__main__":
    predict_demo()
