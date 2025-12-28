import torch 
from torch.utils.data import DataLoader
from pathlib import Path
import cpuinfo

class VADModelTrainer:
    def __init__(self, model, train_ds_path, valid_ds_path, test_ds_path, loss_fn, logger, batch_size):
        self.model = model
        self.logger = logger
        if torch.cuda.is_available():
            self.model.to('cuda')
            self.logger.log(f"Using GPU {torch.cuda.get_device_name(0)} for training")
            self.device = torch.device('cuda')
        else:
            self.logger.log(f"Using CPU {cpuinfo.get_cpu_info()['brand_raw']} for training")
            self.device = torch.device('cpu')
            
        self.loss_fn = loss_fn
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.batch_size = batch_size
        
        self.train_ds_path = train_ds_path
        self.valid_ds_path = valid_ds_path
        self.test_ds_path = test_ds_path
        
        try:
            assert Path(self.train_ds_path).is_file(), f"Training dataset file not found at {self.train_ds_path}"
            assert Path(self.valid_ds_path).is_file(), f"Validation dataset file not found at {self.valid_ds_path}"
            assert Path(self.test_ds_path).is_file(), f"Test dataset file not found at {self.test_ds_path}"
            train_ds_tensors = torch.load(self.train_ds_path, weights_only=True)
            valid_ds_tensors = torch.load(self.valid_ds_path, weights_only=True)
            test_ds_tensors = torch.load(self.test_ds_path, weights_only=True)
            train_ds = torch.utils.data.TensorDataset(*train_ds_tensors)
            valid_ds = torch.utils.data.TensorDataset(*valid_ds_tensors)
            test_ds = torch.utils.data.TensorDataset(*test_ds_tensors)
            self.train_dl = DataLoader(train_ds, batch_size=self.batch_size, shuffle=True)
            self.valid_dl = DataLoader(valid_ds, batch_size=self.batch_size, shuffle=False)
            self.test_dl = DataLoader(test_ds, batch_size=self.batch_size, shuffle=False)
        except Exception as e:
            self.logger.log(f"Error loading .pt files at {self.train_ds_path} or {self.valid_ds_path}: {e}")
            raise
            
    def train(self, num_epochs: int = 20):
        train_acc_hist = [0.0] * num_epochs
        valid_acc_hist = [0.0] * num_epochs

        try:
            for epoch in range(num_epochs):
                self.model.train()
                total_samples = 0
                for x_batch, y_batch in self.train_dl:
                    # move to batch to device
                    x_batch = x_batch.to(self.device)
                    y_batch = y_batch.to(self.device)
                    
                    pred = self.model(x_batch)[:, 0]
                    loss = self.loss_fn(pred, y_batch.float())
                    loss.backward()
                    self.optimizer.step()
                    self.optimizer.zero_grad()

                    is_correct = ((pred >= .5).float() == y_batch).float()
                    train_acc_hist[epoch] += float(is_correct.sum().item())
                    total_samples += y_batch.size(0)
                train_acc_hist[epoch] /= total_samples
                        
                self.model.eval()
                with torch.no_grad():
                    total_samples = 0
                    for x_batch, y_batch in self.valid_dl:
                        # move to batch to device
                        x_batch = x_batch.to(self.device)
                        y_batch = y_batch.to(self.device)

                        pred = self.model(x_batch)[:, 0]
                        is_correct = ((pred>=0.5).float() == y_batch).float()
                        valid_acc_hist[epoch] += float(is_correct.sum().item())
                        total_samples += y_batch.size(0)
                valid_acc_hist[epoch] /= total_samples

                self.logger.log(f"Epoch {epoch + 1}/{num_epochs} - Train Acc: {train_acc_hist[epoch]:.4f}, Valid Acc: {valid_acc_hist[epoch]:.4f}")
                
            # log the results to a graph
            self.logger.log_training_graph(train_acc_hist, valid_acc_hist)
        except Exception as e:
            self.logger.log(f"Error during training: {e}")
            self.logger.log_training_graph(train_acc_hist, valid_acc_hist)
            raise
    
    def evaluate(self):
        self.model.eval()
        test_acc = 0.0
        tot_samples = 0
        with torch.no_grad():
            for x_batch, y_batch in self.test_dl:
                # move to batch to device
                x_batch = x_batch.to(self.device)
                y_batch = y_batch.to(self.device)

                pred = self.model(x_batch)[:, 0]
                is_correct = ((pred>=0.5).float() == y_batch).float()
                test_acc += is_correct.sum()
                tot_samples += y_batch.size(0)
        test_acc /= tot_samples
        self.logger.log(f"Test Accuracy: {test_acc:.4f}")
        
    def save_model(self, save_path: Path) -> None:
        try:
            torch.save(self.model.state_dict(), save_path)
            self.logger.log(f"Model weights saved to {save_path}")
        except Exception as e:
            self.logger.log(f"Error saving model weights to {save_path}: {e}")
            raise