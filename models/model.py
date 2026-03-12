import torch
import torch.nn as nn
import torchvision.models as models

class ScreenshotAuthenticator(nn.Module):
    def __init__(self, num_classes=2, pretrained=True):
        super(ScreenshotAuthenticator, self).__init__()
        # Use MobileNetV2 as it's lightweight and efficient for this task
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        self.backbone = models.mobilenet_v2(weights=weights)
        
        # Replace the classifier layer to output our desired number of classes
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)

    def predict_proba(self, x):
        """Returns the probability of the image being 'fake' (class 1)"""
        self.eval()
        with torch.no_grad():
            outputs = self(x)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            # Assuming class 0 is real, class 1 is fake
            return probabilities[:, 1].item()
