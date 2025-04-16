import numpy as np

class Map:
    def __init__(self):
        self.dict = {
            1 : ['2', 'Hearts'],
            2 : ['3', 'Hearts'],
            3 : ['4', 'Hearts'],
            4 : ['5', 'Hearts'],
            5 : ['6', 'Hearts'],
            6 : ['7', 'Hearts'],
            7 : ['8', 'Hearts'],
            8 : ['9', 'Hearts'],
            9 : ['10', 'Hearts'],
            10 : ['J', 'Hearts'],
            11 : ['Q', 'Hearts'],
            12 : ['K', 'Hearts'],
            13 : ['A', 'Hearts'],
            14 : ['2', 'Diamonds'],
            15 : ['3', 'Diamonds'],
            16 : ['4', 'Diamonds'],
            17 : ['5', 'Diamonds'],
            18 : ['6', 'Diamonds'],
            19 : ['7', 'Diamonds'],
            20 : ['8', 'Diamonds'],
            21 : ['9', 'Diamonds'],
            22 : ['10', 'Diamonds'],
            23 : ['J', 'Diamonds'],
            24 : ['Q', 'Diamonds'],
            25 : ['K', 'Diamonds'],
            26 : ['A', 'Diamonds'],
            27 : ['2', 'Clubs'],
            28 : ['3', 'Clubs'],
            29 : ['4', 'Clubs'],
            30 : ['5', 'Clubs'],
            31 : ['6', 'Clubs'],
            32 : ['7', 'Clubs'],
            33 : ['8', 'Clubs'],
            34 : ['9', 'Clubs'],
            35 : ['10', 'Clubs'],
            36 : ['J', 'Clubs'],
            37 : ['Q', 'Clubs'],
            38 : ['K', 'Clubs'],
            39 : ['A', 'Clubs'],
            40 : ['2', 'Spades'],
            41 : ['3', 'Spades'],
            42 : ['4', 'Spades'],
            43 : ['5', 'Spades'],
            44 : ['6', 'Spades'],
            45 : ['7', 'Spades'],
            46 : ['8', 'Spades'],
            47 : ['9', 'Spades'],
            48 : ['10', 'Spades'],
            49 : ['J', 'Spades'],
            50 : ['Q', 'Spades'],
            51 : ['K', 'Spades'],
            52 : ['A', 'Spades'],
        }

    def get_index(self, rank : str, suit : str):
        for k,v, in self.dict.items():
            if rank == v[0] and suit == v[1]:
                return k - 1
        return -1

