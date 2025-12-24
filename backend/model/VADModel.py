import torch
import torch.nn as nn

class VADModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = self._create_model()
        self.loss_fn = nn.BCELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.batch_size = 32

    def forward(self, x):
        return self.model(x)
    
    def _create_model(self) -> nn.Module:
        model = nn.Sequential()
        
        # convolutional layer 1
        model.add_module(name='conv1', module=nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1))
        model.add_module(name='relu1', module=nn.ReLU())
        model.add_module(name='pool1', module=nn.MaxPool2d(kernel_size=2))
        model.add_module('dropout1', module=nn.Dropout(p=.5))

        model.add_module(name='conv2', module=nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1))
        model.add_module(name='relu2', module=nn.ReLU())
        model.add_module(name='pool2', module=nn.MaxPool2d(kernel_size=2))
        model.add_module('dropout2', module=nn.Dropout(p=.5))

        model.add_module(name='conv3', module=nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1))
        model.add_module('relu3', module=nn.ReLU())        
        model.add_module('pool3', module=nn.MaxPool2d(kernel_size=2))   

        model.add_module(name='conv4', module=nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1))
        model.add_module(name='relu4', module=nn.ReLU())
        
        model.add_module(name='pool4', module=nn.AvgPool2d(kernel_size=5))
        model.add_module(name='flatten', module=nn.Flatten())

        model.add_module(name='fc', module=nn.Linear(in_features=256, out_features=1))
        model.add_module(name='sigmoid', module=nn.Sigmoid())

        return model