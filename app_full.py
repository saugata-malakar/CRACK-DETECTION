"""
Complete Flask Web Application for Concrete Crack Detection
Multi-page with model selection, comparison, and full features
Run: python app_full.py
"""

from flask import Flask, render_template, request, jsonify, session
import torch
from torchvision import transforms
from PIL import Image
import io
import base64
import os
import json
import importlib
from datetime import datetime

# Import model
model_module = importlib.import_module('03_model')
get_model = model_module.get_model

app = Flask(__name__)
app.secret_key = 'concrete-crack-detection-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Available models
MODELS = {
    'resnet18': {
        'name': 'ResNet-18',
        'accuracy': '96-98%',
        'speed': 'Fast',
        'params': '11.3M',
        'description': 'Best balance of speed and accuracy'
    },
    'resnet50': {
        'name': 'ResNet-50',
        'accuracy': '97-99%',
        'speed': 'Medium',
        'params': '25.6M',
        'description': 'Highest accuracy'
    },
    'efficientnet_b0': {
        'name': 'EfficientNet-B0',
        'accuracy': '95-97%',
        'speed': 'Very Fast',
        'params': '4.3M',
        'description': 'Fastest model'
    },
    'vgg16': {
        'name': 'VGG-16',
        'accuracy': '96-98%',
        'speed': 'Slow',
        'params': '121.7M',
        'description': 'Classic architecture'
    }
}

# Global variables
loaded_models = {}
device = None
transform = None

def initialize():
    """Initialize models and transforms"""
    global device, transform
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    print(f"Device: {device}")

def load_model_by_name(model_name):
    """Load a specific model"""
    if model_name in loaded_models:
        return loaded_models[model_name]
    
    print(f"Loading {model_name}...")
    
    # Check for trained checkpoint
    checkpoint_path = f'checkpoints/{model_name}_best.pth'
    if not os.path.exists(checkpoint_path):
        checkpoint_path = 'checkpoints/best_model.pth'
    
    if os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model = get_model(model_name, num_classes=2, pretrained=False)
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        # Use pretrained
        model = get_model(model_name, num_classes=2, pretrained=True)
    
    model = model.to(device)
    model.eval()
    
    loaded_models[model_name] = model
    print(f"✓ {model_name} loaded")
    
    return model

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html', models=MODELS)

@app.route('/predict-page')
def predict_page():
    """Prediction page"""
    return render_template('predict.html', models=MODELS)

@app.route('/compare')
def compare():
    """Model comparison page"""
    return render_template('compare.html', models=MODELS)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/results')
def results():
    """Results/Statistics page"""
    return render_template('results.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for prediction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        model_name = request.form.get('model', 'resnet18')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Load model
        model = load_model_by_name(model_name)
        
        # Read and process image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        predicted_class = 'Cracked' if predicted.item() == 1 else 'Non-cracked'
        confidence_score = confidence.item() * 100
        
        # Convert image to base64
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
            'image': f'data:image/jpeg;base64,{img_str}',
            'model': MODELS[model_name]['name'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare predictions across all models"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Read image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Predict with all models
        results = []
        
        for model_name in MODELS.keys():
            try:
                model = load_model_by_name(model_name)
                
                with torch.no_grad():
                    outputs = model(img_tensor)
                    probs = torch.softmax(outputs, dim=1)
                    confidence, predicted = torch.max(probs, 1)
                
                predicted_class = 'Cracked' if predicted.item() == 1 else 'Non-cracked'
                
                results.append({
                    'model': MODELS[model_name]['name'],
                    'model_key': model_name,
                    'prediction': predicted_class,
                    'confidence': round(confidence.item() * 100, 2),
                    'accuracy': MODELS[model_name]['accuracy'],
                    'speed': MODELS[model_name]['speed'],
                    'probabilities': {
                        'Non-cracked': round(probs[0][0].item() * 100, 2),
                        'Cracked': round(probs[0][1].item() * 100, 2)
                    }
                })
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_str}',
            'results': results,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Concrete Crack Detection - Full Web Application")
    print("="*70)
    
    initialize()
    
    print("\n✅ Server starting...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\nFeatures:")
    print("  • Home page with overview")
    print("  • Single model prediction")
    print("  • Multi-model comparison")
    print("  • Results and statistics")
    print("  • About page")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
