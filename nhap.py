import torch
import torch.nn as nn

# Định nghĩa một mô hình đơn giản với một lớp tuyến tính
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 1)
        self.fc1 = nn.Linear(10, 5)
        self.fc2 = nn.Linear(5, 1)      

    def forward(self, x):
        return self.fc(x)

# Tạo một thể hiện của mô hình
model = SimpleModel()

# Lưu trữ mô hình vào một file .pt
torch.save(model.state_dict(), 'model.pt')