import torch 

class VADModelTrainer:
    def __init__(self, model, train_dl, valid_dl, loss_fn, optimizer, logger):
        self.model = model
        self.train_dl = train_dl
        self.valid_dl = valid_dl
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.logger = logger
    
    def train(self, num_epochs: int = 20):
        train_acc_hist = [0.0] * num_epochs
        valid_acc_hist = [0.0] * num_epochs

        try:
            for epoch in range(num_epochs):
                self.model.train()
                total_samples = 0
                for x_batch, y_batch in self.train_dl:
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
                        pred = self.model(x_batch)[:, 0]
                        is_correct = ((pred>=0.5).float() == y_batch).float()
                        valid_acc_hist[epoch] += float(is_correct.sum().item())
                        total_samples += y_batch.size(0)
                valid_acc_hist[epoch] /= total_samples

                self.logger.log(f"Epoch {epoch + 1}/{num_epochs} - Train Acc: {train_acc_hist[epoch]:.4f}, Valid Acc: {valid_acc_hist[epoch]:.4f}")
            self.logger.log_training_graph(train_acc_hist, valid_acc_hist)
        except Exception as e:
            self.logger.log(f"Error during training: {e}")
            self.logger.log_training_graph(train_acc_hist, valid_acc_hist)
            raise