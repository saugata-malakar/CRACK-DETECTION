"""
CNN Models for Concrete Crack Detection
This script defines various CNN architectures for crack detection
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models


class SimpleCNN(nn.Module):
    """
    Simple CNN architecture for crack detection
    Good baseline model with ~1M parameters
    """
    
    def __init__(self, num_classes: int = 2, dropout: float = 0.5):
        super(SimpleCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(128)
        
        self.conv5 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(256)
        self.conv6 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.bn6 = nn.BatchNorm2d(256)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        # After 3 pooling layers: 256 -> 128 -> 64 -> 32
        self.fc1 = nn.Linear(256 * 32 * 32, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, num_classes)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # Block 1
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = F.relu(self.bn2(self.conv2(x)))
        
        # Block 2
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = F.relu(self.bn4(self.conv4(x)))
        
        # Block 3
        x = self.pool(F.relu(self.bn5(self.conv5(x))))
        x = F.relu(self.bn6(self.conv6(x)))
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully connected
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x


class ResNetCrackDetector(nn.Module):
    """
    ResNet-based crack detector using transfer learning
    Supports ResNet18, ResNet34, ResNet50
    """
    
    def __init__(
        self, 
        num_classes: int = 2, 
        pretrained: bool = True,
        model_name: str = 'resnet18',
        freeze_backbone: bool = False
    ):
        super(ResNetCrackDetector, self).__init__()
        
        # Load pretrained ResNet
        if model_name == 'resnet18':
            self.backbone = models.resnet18(pretrained=pretrained)
            num_features = 512
        elif model_name == 'resnet34':
            self.backbone = models.resnet34(pretrained=pretrained)
            num_features = 512
        elif model_name == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
            num_features = 2048
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Replace final layer
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


class EfficientNetCrackDetector(nn.Module):
    """
    EfficientNet-based crack detector using transfer learning
    """
    
    def __init__(
        self, 
        num_classes: int = 2, 
        pretrained: bool = True,
        model_name: str = 'efficientnet_b0',
        freeze_backbone: bool = False
    ):
        super(EfficientNetCrackDetector, self).__init__()
        
        # Load pretrained EfficientNet
        if model_name == 'efficientnet_b0':
            self.backbone = models.efficientnet_b0(pretrained=pretrained)
            num_features = 1280
        elif model_name == 'efficientnet_b1':
            self.backbone = models.efficientnet_b1(pretrained=pretrained)
            num_features = 1280
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Replace classifier
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


class VGGCrackDetector(nn.Module):
    """
    VGG-based crack detector using transfer learning
    """
    
    def __init__(
        self, 
        num_classes: int = 2, 
        pretrained: bool = True,
        model_name: str = 'vgg16',
        freeze_backbone: bool = False
    ):
        super(VGGCrackDetector, self).__init__()
        
        # Load pretrained VGG
        if model_name == 'vgg16':
            self.backbone = models.vgg16(pretrained=pretrained)
        elif model_name == 'vgg19':
            self.backbone = models.vgg19(pretrained=pretrained)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.features.parameters():
                param.requires_grad = False
        
        # Replace classifier
        num_features = self.backbone.classifier[0].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Linear(num_features, 4096),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(4096, 1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


def get_model(
    model_name: str = 'simple_cnn',
    num_classes: int = 2,
    pretrained: bool = True,
    freeze_backbone: bool = False
) -> nn.Module:
    """
    Factory function to get a model by name
    
    Args:
        model_name: Name of the model architecture
        num_classes: Number of output classes
        pretrained: Whether to use pretrained weights (for transfer learning models)
        freeze_backbone: Whether to freeze backbone weights
    
    Returns:
        PyTorch model
    """
    
    model_name = model_name.lower()
    
    if model_name == 'simple_cnn':
        model = SimpleCNN(num_classes=num_classes)
    
    elif model_name in ['resnet18', 'resnet34', 'resnet50']:
        model = ResNetCrackDetector(
            num_classes=num_classes,
            pretrained=pretrained,
            model_name=model_name,
            freeze_backbone=freeze_backbone
        )
    
    elif model_name in ['efficientnet_b0', 'efficientnet_b1']:
        model = EfficientNetCrackDetector(
            num_classes=num_classes,
            pretrained=pretrained,
            model_name=model_name,
            freeze_backbone=freeze_backbone
        )
    
    elif model_name in ['vgg16', 'vgg19']:
        model = VGGCrackDetector(
            num_classes=num_classes,
            pretrained=pretrained,
            model_name=model_name,
            freeze_backbone=freeze_backbone
        )
    
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    return model


def count_parameters(model: nn.Module) -> dict:
    """Count trainable and total parameters in a model"""
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total': total_params,
        'trainable': trainable_params,
        'frozen': total_params - trainable_params
    }


def test_models():
    """Test all model architectures"""
    
    print("\n" + "="*70)
    print("Testing Model Architectures")
    print("="*70)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    
    models_to_test = [
        ('simple_cnn', False, False),
        ('resnet18', True, False),
        ('resnet18', True, True),
        ('efficientnet_b0', True, False),
        ('vgg16', True, False),
    ]
    
    # Test input
    batch_size = 4
    test_input = torch.randn(batch_size, 3, 256, 256).to(device)
    
    print(f"\nTest input shape: {test_input.shape}\n")
    
    for model_name, pretrained, freeze in models_to_test:
        print("-" * 70)
        
        model_desc = model_name
        if pretrained:
            model_desc += " (pretrained)"
        if freeze:
            model_desc += " [frozen backbone]"
        
        print(f"Model: {model_desc}")
        
        try:
            # Create model
            model = get_model(
                model_name=model_name,
                num_classes=2,
                pretrained=pretrained,
                freeze_backbone=freeze
            )
            model = model.to(device)
            model.eval()
            
            # Count parameters
            params = count_parameters(model)
            print(f"  Total parameters:     {params['total']:,}")
            print(f"  Trainable parameters: {params['trainable']:,}")
            if params['frozen'] > 0:
                print(f"  Frozen parameters:    {params['frozen']:,}")
            
            # Test forward pass
            with torch.no_grad():
                output = model(test_input)
            
            print(f"  Output shape:         {output.shape}")
            print(f"  ✓ Forward pass successful")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ Model testing complete!")
    print("="*70)


if __name__ == "__main__":
    test_models()
