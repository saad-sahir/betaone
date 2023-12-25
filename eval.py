import numpy as np

history = []
current_position = ""

def getFEN(fen, _print=False):
    global current_position
    if current_position == "":
        current_position = fen
    if fen not in history:
        history.append(fen)
        print(eval_pos1(fen))
        if _print == True:
            print(fen)
    else:
        pass

def count_score(fen):  # just counts the number of pieces in and assigns a value
    counts = {'K': 0, 'Q': 0, 'R': 0, 'B': 0, 'N': 0, 'P': 0, 'k': 0, 'q': 0, 'r': 0, 'b': 0, 'n': 0, 'p': 0}
    for char in fen.split(' ')[0]:
        if char in counts:
            counts[char] += 1
    
    return (
        200 * (counts['K'] - counts['k']) +
        9 * (counts['Q'] - counts['q']) +
        5 * (counts['R'] - counts['r']) +
        3 * (counts['B'] - counts['b'] + counts['N'] - counts['n']) +
        1 * (counts['P'] - counts['p'])
    )



def eval_pos1(fen):
    count_score = count_score(fen)
    return count_score