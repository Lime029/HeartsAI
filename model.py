import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class DQN (nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.input_layer = nn.Linear(3 * 52, 1024)    # input = [1 x (3 * 52)]
        self.hidden_1 = nn.Linear(1024, 512)
        self.hidden_2 = nn.Linear(512, 512)
        self.hidden_3 = nn.Linear(512, 256)
        self.hidden_4 = nn.Linear(256, 3 * 52)
        self.hidden_output_layer = nn.Linear(3* 52, 1)  # output = [1 x 1]

        self.optimiser = optim.Adam(self.parameters(), lr=0.001)
        self.loss = nn.MSELoss()

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, state): 
        ''' 
        State should be in the shape (1, 3*52). 
        The first 52 are the cards in the agent's hand 
        The second 52 are the cards observed in play so far
        The third 52 is a one hot encoding of the action we intend to play

        Model outputs a single value --> expected reward from a (state, action) pair
        '''
        x = F.relu(self.input_layer(state))
        x = F.relu(self.hidden_1(x))
        x = F.relu(self.hidden_2(x))
        x = F.relu(self.hidden_3(x))
        x = F.relu(self.hidden_4(x))
        return self.hidden_output_layer(x)