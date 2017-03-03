# coding: utf-8
## This notebook contains my code from Will Tipton's "Solving Poker" video series

import os
import rayeval as re
import scipy.misc

# Load RayEval data
re.load_handranks_7('/anaconda/shared/rayeval_hand_ranks_7.dat')

# Define some useful constants
numCards = 52
numRanks = 13
numSuits = 4
numHands = 1326 # nchoosek(52,2)
numVillainHands = 1225 # nchoosek(50,2)

# Make some lists
# suits = ['h', 'd', 'c', 's']
# ranks = ['A', 'K', 'Q','J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
# cards = ['2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah',
#          '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad',
#          '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac',
#          '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As']


# RayEval's version of card transformation formulas
def string2card(cards):
    newcards = []
    for i in cards:
        newcards.append(re.card_to_rank(i))
    return newcards

def card2string(cards):
    newcards = []
    for i in cards:
        newcards.append(re.rank_to_card(i))
    return newcards

# We can describe hands or the board as lists of strings, where '__' represents an unknown card
handAsStrings = ['Ah', 'Jd']
boardAsStrings = ['8d', '6s', '3h', 'Kd', '__']

# We can also give each card a number and describe hands or boards as lists of numbers
# Convention: always work with the numerical representation of hands and boards
#    Convert to strings at the last minute whenever it's necessary, and we'll indicate the stringness
#    in the variable name.  Whenever we want to manually input hand or board, we'll need to convert
# Notice that cards run from 0 to 51, while empty card gets 255
hand = string2card(handAsStrings)
board = string2card(boardAsStrings)

#  Let's write our own function!  It's good practice to document the inputs and outputs of functions.
#  It will be useful to have a function that takes as input two lists of cards, and tells us
#  if the two lists overlap at all.  To do this, look at every pair of cards and check if equal
#  Input:
#      cards1, cards2 - lists of cards represented as numbers
#  Output:
#    True if the lists conflict and False otherwise
#  NB: Indentation matters.
#  Note:  We don't return true if we find a match for the empty card (255).
def conflicts(cards1, cards2):
    for i in cards1:
        for j in cards2:
            try:
                c1 = string2card([i])[0]
            except:
                c1 = i
            try:
                c2 = string2card([j])[0]
            except:
                c2 = j
            if c1 == c2 and c1 < numCards:
                return True
    return False

#  Note that the conflicts function is _globally_ accessible

# Test the functions we made
conflicts(board, [45, 5])
villainHand = string2card(['As', '4s'])
peresult = re.eval_mc(game='holdem', pockets=[hand, villainHand], board = board, iterations=100000)


# Compute an equity using RayEval and make a function to take care of the details
# Inputs:
#     hands and villainHand - lists of cards in numerical format describing two hands
#     board - list of cards describing the board
# Output: all-in equity of hand vs villainHand on board
#         -1 if any of hand, villainHand, and board conflict

def getEquityVsHand(hand, villainHand, board):
    if conflicts(hand,villainHand) or conflicts(hand,board) or conflicts(board,villainHand):
        return -1
    peresult = re.eval_mc(game='holdem', pockets=[hand, villainHand], board = board, iterations=100000)
    return peresult[0]

# Test function
hand1 = string2card(['Ah', 'Jd'])
hand2 = string2card(['4c', '3s'])
getEquityVsHand(hand1, hand2, board)

# To avoid expensive equity calculations, we will pre-compute all equities for any
# board we are interested in.
# Essentially, we'll make a table that contains all hand-vs-hand matchups, and we'll computer
# the equity of every matchup once.  And then if we need it in the future, we can just look it up.

# EquityArray class organizes hand vs hand equities for a board
class EquityArray:
    # Constructor
    # Input:
    #    b - list of numbers representing a board
    def __init__(self, b):
        self.board = b
        self.eArray = numpy.zeros((numCards,numCards,numCards,numCards))
        if os.path.isfile(self.getFilename()):
            self.eArray = numpy.load(self.getFilename())
        else:
            self.makeArray()

    def makeArray(self): #can you cut down on hand combos here through only considering isomorphic combos?
        x = 0
        for i in range(numCards):
            for j in range (numCards):
                for a in range(numCards):
                    for b in range(numCards):
                        x += 1
                        hand = [i, j]
                        villainHand = [a, b]
                        self.eArray[i][j][a][b] = getEquityVsHand(hand, villainHand, self.board)
                        print x
        numpy.save(self.getFilename(), self.eArray)

    # Output: filename built from self.board
    # For example, if card2string(self.board) == ['Ah', 'Jd', '2c', '__','__']
    # then x return 'AhJd2c.ea.npy'.
    def getFilename(self):
        boardStr = ''
        boardAsStrings = card2string(self.board)
        for i in boardAsStrings:
            if i != '__':
                boardStr = boardStr + i
            if boardStr == '': #this is the case when we have the preflop board
                boardStr = 'preflop'
        boardStr = boardStr + '.ea.npy'
        return boardStr


# Test function
print "Equity (" + card2string(hand) " vs " + card2string(villHand) + " on " + /
      card2string(board) + getEquityVsHand(hand, villHand, board)

# EquityArray(board)
