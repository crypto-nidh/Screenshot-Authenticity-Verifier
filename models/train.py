import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from models.dataset import ScreenshotDataset, get_transforms
from models.model import ScreenshotAuthenticator

def train_model(data_dir='dataset', epochs=10, batch_size=32, lr=0.001, save_path='models/saved_model.pth'):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 1. Load Data
    transform = get_transforms()
    full_dataset = ScreenshotDataset(root_dir=data_dir, transform=transform)
    
    if len(full_dataset) == 0:
        print("Warning: Dataset is empty. Cannot train. Please add images to dataset/real and dataset/fake.")
        return

    # Split into train/val
    val_size = int(0.2 * len(full_dataset))
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 2. Initialize Model
    model = ScreenshotAuthenticator(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # 3. Training Loop
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Validation
        model.eval()
        correct = 0
        total = 0
        val_loss = 0.0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_acc = 100 * correct / max(total, 1)
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {running_loss/max(len(train_loader), 1):.4f} - "
              f"Val Loss: {val_loss/max(len(val_loader), 1):.4f} - Val Acc: {val_acc:.2f}%")

        # Save best model
        if val_acc >= best_val_acc and len(train_dataset) > 0:
            best_val_acc = val_acc
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            torch.save(model.state_dict(), save_path)
            print(f"Saved best model with accuracy: {best_val_acc:.2f}%")

    print("Training complete.")

if __name__ == "__main__":
    train_model()
