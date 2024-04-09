import torch

model = torch.nn.Linear(2, 1)
torch.save(model, "model2.pt")
