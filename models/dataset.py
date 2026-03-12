import os
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms

class ScreenshotDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        """
        Args:
            root_dir (string): Directory with all the images. Should contain 'real' and 'fake' subfolders.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.root_dir = root_dir
        self.transform = transform
        self.classes = ['real', 'fake']
        self.image_paths = []
        self.labels = []

        for label_idx, class_name in enumerate(self.classes):
            class_dir = os.path.join(root_dir, class_name)
            if not os.path.exists(class_dir):
                print(f"Warning: Directory {class_dir} does not exist.")
                continue
            
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.image_paths.append(os.path.join(class_dir, img_name))
                    self.labels.append(label_idx)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a blank image as fallback for corrupted files
            image = Image.new('RGB', (224, 224))
            
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label

def get_transforms(img_size=224):
    """Returns standard image transforms for training/evaluation"""
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
