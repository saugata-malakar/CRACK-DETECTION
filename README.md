# 🏗️ Concrete Crack Detection using Deep Learning

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.9+-red.svg)](https://pytorch.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-Powered Structural Health Monitoring System**

🌐 **Live Demo:** [https://crack-detection-6j4c.onrender.com/](https://crack-detection-6j4c.onrender.com/)


---

## 🎯 Overview

A complete deep learning pipeline for detecting cracks in concrete structures using state-of-the-art CNNs. Achieves **97% accuracy** on the SDNET2018 dataset with 56,092 images.

### ✨ Key Features

- 🤖 **4 CNN Models** - ResNet, EfficientNet, VGG, Custom
- ⚡ **Real-time Detection** - 50ms inference time
- 📊 **Model Comparison** - Compare all models simultaneously
- 🎨 **Beautiful Web UI** - Multi-page responsive interface
- 🚀 **GPU Accelerated** - CUDA support
- 📈 **97% Accuracy** - State-of-the-art performance

---

## 📊 Dataset: SDNET2018

- **Total Images:** 56,092 (256×256 px)
- **Categories:** Bridge Decks, Walls, Pavements
- **Classes:** Cracked (15.1%) and Non-cracked (84.9%)
- **Crack Width:** 0.06 mm to 25 mm

### Dataset Structure
```
├── Decks/      13,620 images (2,025 cracked)
├── Pavements/  24,334 images (2,608 cracked)
└── Walls/      18,138 images (3,851 cracked)
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/saugata-malakar/concrete-crack-detection.git
cd concrete-crack-detection

# Install dependencies
pip install -r requirements.txt
```

### Run Web Application

```bash
# Start the web app
python app_full.py

# Open browser
http://localhost:5000
```

### 2-Minute Demo

```bash
# Quick demo (trains on small subset)
python 06_train_2min_demo.py
python 07_evaluate_demo.py
python 08_predict_demo.py
```

---

## 🌐 Live Demo

**🔗 Deployed Application:** [https://concrete-crack-detection-nine.vercel.app](https://concrete-crack-detection-nine.vercel.app)

**Features:**
- 🏠 Home - Overview and statistics
- 🔮 Predict - Upload and detect cracks
- ⚖️ Compare - Compare all 4 models
- 📊 Results - Performance metrics
- ℹ️ About - Project information

---

## 📁 Project Structure

```
concrete-crack-detection/
├── 📊 Data Pipeline
│   ├── 01_data_analysis.py
│   ├── 02_data_loader.py
│   └── 04_train_val_test_split.py
│
├── 🤖 Models
│   └── 03_model.py (4 architectures)
│
├── 🎨 Augmentation
│   └── 05_data_augmentation.py
│
├── 🏋️ Training
│   ├── 06_train.py (full training)
│   └── 06_train_2min_demo.py (quick demo)
│
├── 📈 Evaluation
│   ├── 07_evaluate.py
│   └── 07_evaluate_demo.py
│
├── 🔮 Prediction
│   ├── 08_predict.py
│   └── 08_predict_demo.py
│
├── 🌐 Web Application
│   ├── app_full.py (Flask backend)
│   └── templates/ (HTML pages)
│
└── 📚 Documentation
    ├── README.md
    ├── QUICK_START.md
    ├── TRAINING_SUMMARY.md
    └── DEPLOYMENT_FINAL.md
```

---

## 🤖 Model Architectures

| Model | Accuracy | Parameters | Speed | Recommendation |
|-------|----------|------------|-------|----------------|
| **ResNet-18** ⭐ | 96-98% | 11.3M | Fast | **Best Choice** |
| ResNet-50 | 97-99% | 25.6M | Medium | Highest Accuracy |
| EfficientNet-B0 | 95-97% | 4.3M | Very Fast | Fastest |
| VGG-16 | 96-98% | 121.7M | Slow | Classic |

---

## 💻 Usage

### Training a Model

```python
# Simple training
python 06_train.py

# Custom configuration
config = {
    'model_name': 'resnet18',
    'batch_size': 32,
    'num_epochs': 30,
    'learning_rate': 0.001
}
```

### Making Predictions

```python
from predict import CrackPredictor

# Initialize
predictor = CrackPredictor('checkpoints/best_model.pth')

# Predict
result = predictor.predict_image('test.jpg')
print(f"Prediction: {result['predicted_class']}")
print(f"Confidence: {result['confidence']*100:.2f}%")
```

### Web Application

```python
# Start Flask app
python app_full.py

# Access at: http://localhost:5000
```

---

## 📈 Results

### Performance Metrics (ResNet-18)

```
✅ Accuracy:    97.2%
✅ Precision:   94.5%
✅ Recall:      91.3%
✅ F1-Score:    92.9%
✅ ROC AUC:     0.978
```

### Training Time

- **ResNet-18:** 30-45 minutes (GPU)
- **EfficientNet-B0:** 25-40 minutes (GPU)
- **ResNet-50:** 60-90 minutes (GPU)

---

## 🎨 Features

### Data Augmentation

```python
✅ Random Horizontal/Vertical Flip
✅ Random Rotation (±15°)
✅ Color Jitter
✅ Random Affine
✅ Random Perspective
```

### Training Features

```python
✅ Early Stopping
✅ Learning Rate Scheduling
✅ Model Checkpointing
✅ GPU Acceleration
✅ Progress Tracking
```

---

## 🌐 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### GitHub Pages

```bash
# Push to GitHub
git push origin main

# Enable Pages in Settings
```

### Local Server

```bash
python app_full.py
# Access: http://localhost:5000
```

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- **[Training Guide](TRAINING_SUMMARY.md)** - Detailed training instructions
- **[Deployment Guide](DEPLOYMENT_FINAL.md)** - Deploy to Vercel/Heroku
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete feature list

---

## 🎓 Use Cases

### Research
- Benchmark different architectures
- Test augmentation strategies
- Explore transfer learning

### Education
- Learn PyTorch and deep learning
- Understand CNN architectures
- Practice model evaluation

### Production
- Deploy crack detection system
- Integrate with inspection workflows
- Automate structural health monitoring

---

## 🔧 Requirements

```txt
Python >= 3.8
torch >= 1.9.0
torchvision >= 0.10.0
Flask >= 2.3.0
numpy >= 1.19.0
Pillow >= 8.0.0
matplotlib >= 3.3.0
scikit-learn >= 0.24.0
```

---

## 📊 Dataset Citation

```bibtex
@article{dorafshan2018sdnet2018,
  title={SDNET2018: An annotated image dataset for training deep learning-based concrete crack detection algorithms},
  author={Dorafshan, Sattar and Thomas, Robert J and Maguire, Marc},
  journal={Data in brief},
  volume={21},
  pages={1664--1668},
  year={2018},
  publisher={Elsevier}
}
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional model architectures
- [ ] Advanced augmentation techniques
- [ ] Mobile app deployment
- [ ] Real-time video processing
- [ ] Multi-class classification

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Dataset:** SDNET2018 by Utah State University
- **Framework:** PyTorch
- **Models:** ResNet, EfficientNet, VGG
- **Deployment:** Vercel, GitHub Pages

---

## 📞 Contact

- **Author:** Saugata Malakar
- **GitHub:** [@saugata-malakar](https://github.com/saugata-malakar)
- **Project:** [Concrete Crack Detection](https://github.com/saugata-malakar/concrete-crack-detection)
- **Live Demo:** [https://concrete-crack-detection-nine.vercel.app](https://concrete-crack-detection-nine.vercel.app)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ for Structural Health Monitoring**

[🌐 Live Demo](https://concrete-crack-detection-nine.vercel.app) • [📖 Documentation](QUICK_START.md) • [🐛 Report Bug](https://github.com/saugata-malakar/concrete-crack-detection/issues)

</div>
