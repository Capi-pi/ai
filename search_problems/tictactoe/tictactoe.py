"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X
    else:
        count_x, count_o = 0, 0
        for i in range(3):
            for j in range(3):
                if board[i][j] == X:
                    count_x += 1
                elif board[i][j] == O:
                    count_o += 1
        if count_x > count_o:
            return O
        else:
            return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        return None
    else:
        board_copy = copy.deepcopy(board)
        i, j = action[0], action[1]
        board_copy[i][j] = player(board)
        return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in board:
        if row[0] == row[1] == row[2] in (X, O):
            return row[0]

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] in (X, O):
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] in (X, O):
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] in (X, O):
        return board[0][2]

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == None:
        c = 0
        for row in board:
            for cell in row:
                if cell == EMPTY:
                    return False
                else:
                    c += 1
        if c == 9:
            return True
    else:
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def alpha_beta(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    def max_value(state, alpha, beta):
        
        v = float("-inf")
        if terminal(state):
            return utility(state)
        for action in actions(state):
            v = max(v, min_value(result(state, action), alpha, beta)) 
            alpha = max(alpha, v)
            if alpha >= beta:               #si le min garantit pour le max est plus grand que le max garantit pour le joueur min 
                                            #alors STOP on arrête des regarder les autres possibilités
                return v
        return v

    def min_value(state, alpha, beta):
        v = float("inf")
        if terminal(state):
            return utility(state)
        for action in actions(state):
            v = min(v, max_value(result(state, action), alpha, beta))
            beta = min(beta, v)
            if beta <= alpha:               #si le min garantit pour le max est plus grand que le max garantit pour le joueur min 
                                            #alors STOP on arrête des regarder les autres possibilités
                return v
        return v
    
    if player(board) == X:
        v = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        action = (0, 0)
        for a in actions(board):
            candidate = min_value(result(board, a), alpha, beta)
            if v < candidate:
                v = candidate
                action = a 
        return action 
    
    elif player(board) == O:
        alpha = float("-inf")
        beta = float("inf")
        v = float("inf")
        action = (0, 0)
        for a in actions(board):
            candidate = max_value(result(board, a), alpha, beta)
            if v > candidate:
                v = candidate
                action = a 
        return action 
    

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    def max_value(state):
        v = float("-inf")
        if terminal(state):
            return utility(state)
        for action in actions(state):
            v = max(v, min_value(result(state, action))) 
        return v

    def min_value(state):
        v = float("inf")
        if terminal(state):
            return utility(state)
        for action in actions(state):
            v = min(v, max_value(result(state, action)))
        return v
    
    if player(board) == X:
        v = float("-inf")
        action = (0, 0)
        for a in actions(board):
            if v < min_value(result(board, a)):
                v = min_value(result(board, a))
                action = a 
        return action 
    
    elif player(board) == O:
        v = float("inf")
        action = (0, 0)
        for a in actions(board):
            if v > max_value(result(board, a)):
                v = max_value(result(board, a))
                action = a 
        return action 