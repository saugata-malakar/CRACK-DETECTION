"""
Flask Web Application for Concrete Crack Detection
Run: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import torch
from torchvision import transforms
from PIL import Image
import io
import base64
import os
import importlib

# Import model
model_module = importlib.import_module('03_model')
get_model = model_module.get_model

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global model variable
model = None
device = None
transform = None

def load_model():
    """Load the trained model"""
    global model, device, transform
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Check if demo model exists
    if os.path.exists('checkpoints_demo/demo_model.pth'):
        checkpoint_path = 'checkpoints_demo/demo_model.pth'
        print("Loading demo model...")
    elif os.path.exists('checkpoints/best_model.pth'):
        checkpoint_path = 'checkpoints/best_model.pth'
        print("Loading full model...")
    else:
        print("No trained model found. Using pretrained ResNet-18...")
        model = get_model('resnet18', num_classes=2, pretrained=True)
        model = model.to(device)
        model.eval()
        
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        return
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model = get_model('resnet18', num_classes=2, pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    print(f"Model loaded successfully on {device}")

@app.route('/')
def index():
    """Home page"""
    return render_template('app.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict crack in uploaded image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        
        # Transform image
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        predicted_class = 'Cracked' if predicted.item() == 1 else 'Non-cracked'
        confidence_score = confidence.item() * 100
        
        # Convert image to base64 for display
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'prediction': predicted_class,
            'confidence': round(confidence_score, 2),
            'probabilities': {
                'Non-cracked': round(probs[0][0].item() * 100, 2),
                'Cracked': round(probs[0][1].item() * 100, 2)
            },
            'image': f'data:image/jpeg;base64,{img_str}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Concrete Crack Detection Web App")
    print("="*60)
    
    # Load model
    load_model()
    
    print("\n✅ Server starting...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
