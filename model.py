import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class DQN (nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.input_hidden_connected_layer = nn.Linear(2 * 52, 1024)
        self.hidden_hidden_connected_layer_1 = nn.Linear(1024, 512)
        self.hidden_hidden_connected_layer_2 = nn.Linear(512, 416)
        self.hidden_hidden_connected_layer_3 = nn.Linear(416, 256)
        self.hidden_hidden_connected_layer_4 = nn.Linear(256, 2 * 52)
        self.hidden_output_connected_layer = nn.Linear(2 * 52, self.n_actions)

        self.optimiser = optim.Adam(self.parameters(), lr=0.001)
        self.loss = nn.SmoothL1Loss()

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cuda:1')
        self.to(self.device)

    def forward(self, state):
        # state should be in the shape (1, 2*52). 
        # the first 52 are the cards in the agent's hand 
        # the second 52 are the cards observed in play so far
        
        x = F.relu(self.input_hidden_connected_layer(state))
        x = F.relu(self.hidden_hidden_connected_layer_1(x))
        x = F.relu(self.hidden_hidden_connected_layer_2(x))
        x = F.relu(self.hidden_hidden_connected_layer_3(x))
        x = F.relu(self.hidden_hidden_connected_layer_4(x))
        return self.hidden_output_connected_layer(x)
    
    #state = T.Tensor(observation).to(self.device).reshape(-1, 2*52)
