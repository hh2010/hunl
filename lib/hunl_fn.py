import os
import sys
import rayeval as re
import scipy.misc
import pydot
import numpy
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pylab, mlab, pyplot
from pylab import *

# Define some useful constants
numCards = 52
numRanks = 13
numSuits = 4
numHands = 1326 # nchoosek(52,2)
numVillainHands = 1225 # nchoosek(50,2)

# Make some lists
suits = ['h', 'd', 'c', 's']
ranks = ['A', 'K', 'Q','J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
cards = ['2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah',
         '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad',
         '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac',
         '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As']

def pe_string2card(cards_inp):
    """ Convert cards string to number """
    newcards = []
    for i in cards_inp:
        if i in ['__', '_', '*']:
            newcards.append(255)
        else:
            newcards.append(cards.index(i))
    return newcards

def pe_card2string(cards_inp):
    """ Convert cards number to string """
    newcards = []
    for i in cards_inp:
        if i == 255:
            newcards.append('__')
        else:
            newcards.append(cards[i])
    return newcards

def conflicts(cards1, cards2):
    """ Test of hand conflicts with other hand, or board """
    for i in cards1:
        for j in cards2:
            if i == j and i < numCards:
                return True
    return False

### Set up EquityArray class ###
class EquityArray:
    """
    Constructor
    Input:
    b - list of numbers representing a board
    """
    def __init__(self, b):
        self.board = b
        self.eArray = numpy.zeros((numCards,numCards,numCards,numCards))
        if os.path.isfile('eqarray/' + self.getFilename()):
            self.eArray = numpy.load('eqarray/' + self.getFilename())
        else:
            self.makeArray()

    def makeArray(self):
        """
        Until we figure out a way to computer this faster, only load from
        EquityArrays created from Ubuntu instance
        """
        print("ERROR! Cannot make new EquityArrays on this system")
        sys.exit()

    # Output: filename built from self.board
    # For example, if card2string(self.board) == ['Ah', 'Jd', '2c', '__','__']
    # then x return 'AhJd2c.ea.npy'.
    def getFilename(self):
        """
        Get the filename of equity array, and load it if file exists
        """
        boardStr = ''
        boardAsStrings = pe_card2string(self.board)
        for i in boardAsStrings:
            if i != '__':
                boardStr = boardStr + i
            if boardStr == '': #this is the case when we have the preflop board
                boardStr = 'preflop'
        boardStr = boardStr + '.ea.npy'
        return boardStr

# Define EquityArray functions
def getEquityVsHandFast(hand, villainHand, ea):
    return ea.eArray[hand[0]][hand[1]][villainHand[0]][villainHand[1]]

def setHandsWithConflicts(handArray, cardslist, num):
    """ How to handle when hand had conflicts """
    for c in cardslist:
        if c < numCards:
            handArray[c,:] = num
            handArray[:,c] = num

def zeroHandsWithConflicts(handArray, cardslist):
    """ Set number of combos of hands with conflicts to 0 """
    setHandsWithConflicts(handArray, cardslist, 0)

### Create the Range class ###
class Range:
    """
    Range class describes a poker hand range
    The data:
    a numpy array of sides numCards by numCards, r, of numbers between 0 and 1,
      each of which describes the fraction of a particular hand in the range
    Note: there is some redundancy in our representation.  For example, (3h, 2h) - (2h, 3h)
    We are only going to access elements of r, r[i][j] such that j > 1
    """
    def __init__(self, initFrac = None):
        """ Create the class and set all combos to zero """
        self.r = numpy.zeros((numCards, numCards))
        if initFrac != None:
            self.setAllFracs(initFrac)

    def getFrac(self, hand):
        """
        Input: a hand represented by a list of two numbers
        Output: the fraction of the hand contained in the range
        Side-effects: N/A
        """
        card1, card2 = hand
        if card1 > card2:
            card1,card2 = card2,card1
        return self.r[card1][card2]

    def getNumHands(self):
        """
        Input: N/A
        Output: total number of hand combinations contained in the range
        Side-effects: N/A
        """
        return sum(self.r)

    def getNumHandsWithoutConflicts(self, cardslist):
        """
        Input: cardslist - list in numerical format
        Output: the number of hand combos in the range that do not conflict with cardslist
        Side-effects: N/A
        """
        temp = numpy.copy(self.r)
        zeroHandsWithConflicts(temp, cardslist)
        return sum(temp)

    def removeHandsWithConflicts(self, cardslist):
        """
        Input: cardslist - list in numerical format
        Output: N/A
        Side-effects: removes hands from range that conflict with cards in cardslist
        """
        zeroHandsWithConflicts(self.r, cardslist)

    def setFrac(self, hand, f):
        """
        Inputs:
          hand - list of numbers describing a hand
          f - fraction
        Output: N/A
        Side-effects: sets the fraction of hand in the range to f
        """
        card1, card2 = hand
        if card1 > card2:
            card1,card2 = card2,card1
        self.r[card1][card2] = f

    def setAllFracs(self, num):
        """
        Input: num - a fraction
        Output: N/A
        Side-effects: set the fraction of all hand combos to num
        """
        for i in range(numCards):
            for j in range(i+1, numCards):
                self.r[i][j] = num

    def scaleFracs(self, num):
        """
        Input: num - a fraction
        Output: N/A
        Side-effect: scale the fraction of every hand combo by num
        NB: We haven't always performed great input validation.  For example, here it is up to
          the user of the function to ensure that the scaling number does not change any of the fractions
          to be less than 0 or greater than 1.
        """
        self.r = self.r * num



    def setRangeString(self, rangeString, value):
        """
        Input:
          - rangeString - string containing comma-separated terms of the form XX, XY, XYs, XYo, XaYb
          - value - a fraction
        Output: N/A
        Side-effects: set hand combos specified by the range string to values
        """
        handStrs = rangeString.replace(' ','').split(',')
        for hand in handStrs:
            if len(hand) == 2:
                rank1 = hand[0]
                rank2 = hand[1]
                for i in suits:
                    for j in suits:
                        if rank1 == rank2 and i == j : # avoid stuff like 2c2c
                            continue
                        self.setFrac(pe_string2card([rank1+i, rank2+j]), value)
            elif len(hand) == 3:
                rank1 = hand[0]
                rank2 = hand[1]
                if rank1 == rank2:
                    print("ERROR! Cannot have suited pocket pair")
                if hand[2] == 's': # suited hands
                    for s in suits:
                        self.setFrac(pe_string2card([rank1+s, rank2+s]), value)
                else: # unsuited hands
                    for i in range(numSuits):
                        for j in range(i+1, numSuits):
                            self.setFrac(pe_string2card([rank1+suits[i], rank2+suits[j]]), value)
            elif len(hand) == 4:
                card1 = hand[0:2]
                card2 = hand[2:4]
                self.setFrac(pe_string2card([card2, card2]), value)
            else:
                print("ERROR! Hand input needs to be 2 to 4 characters")

    def getAmbigFrac(self, rank1, rank2, suited):
        """
        Input:
         - rank1 - a string specifying a rank ('2', '3', 'T', 'A')
         - rank2 - similar
         - suited - a boolean (True, False) indicating suitedness
        Output: fraction of specified ambiguous hand contained in the rank
        Side-effects: N/A

        Ambiguous hands are, e.g., AKo (12 combos)
                                   AKs (4 combos)
                                   33 (6 combos)
        So for example, if we call getAmbigFrac('A', 'K', True), we're interested
        in AKs, and if the range contains 100% of AKhh and AKss, but none of AKcc
        or AKdd, the result should be 0.5 (not 2).
        Note: if we're interested in pocket pairs then rank1 == rank2 and suited == False
        """
        nHand = 0.0
        nFrac = 0.0

        # look at every specific hand combo corresponding to rank1, rank 2 and suited
        for i in suits:
            for j in suits:
                card1 = rank1 + i
                card2 = rank2 + j
                if (suited and i != j) or (not suited and i == j):
                    continue
                if (card1 == card2):
                    continue
                nHand += 1 # short for nHand = nHand + 1
                nFrac += self.getFrac(pe_string2card([card1,card2]))
        return nFrac / nHand

    def _repr_svg_(self):
        """ iPython special function - represent as scalable vector graphic """
        result = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="260" height="260">'
        for i in range(numRanks):
            for j in range(numRanks):
                frac = self.getAmbigFrac(ranks[i], ranks[j], i > j)
                hexcolor = '#%02x%02x%02x' % (255*(1-frac), 255, 255*(1-frac))
                result += '<rect x="' + str(i*20) + '" y="' + str(j*20) + '" width="20" height="20" fill="' + hexcolor+'"></rect>'
                result += '<text x=' + str(i*20)+' y='+str((j+1)*20) + ' font-size=12>' + ranks[i]\
                          + ranks[j] + '</text>'
        result += '</svg>'
        return result

    def getHandsSortedAndEquities(self, villainRange, board):
        """
        Input:
          villainRange - Range object
          board - list of 5 numbers describing a board
        Output: list of tuples of the form (hand, equity)
                              where a hand is a list of integers and equity is
                              equity vs villainRange on board.  This output list
                              will be sorted by equity (highest first).
        Side-effects: N/A
        """
        ea = EquityArray(board)
        result = []
        for i in range(numCards):
            for j in range(i+1, numCards):
                hand = [i,j]
                if not conflicts(board,hand):
                    result.append((hand, getEquityVsRange(hand, villainRange, ea)))
        result.sort(key = lambda x: x[1], reverse = True)
        return result

    def setToTop(self, fraction, board):
        """
        Input:
         fraction - a number describing fraction of all hands
         board - a list of numbers representing a board
        Output: N/A
        Side-effects: set fraction of (approx.) the top fraction of hands (as ranked by equity vs ATC) on board to 1, and the rest to 0
        """
        rangeAllHands = Range()
        rangeAllHands.setAllFracs(1.0) # ATC range
        handsSorted = self.getHandsSortedAndEquities(rangeAllHands, board)

        numCardsLeft = numCards
        for c in board:
            if c < numCards:
                numCardsLeft -= 1
        self.setAllFracs(0)
        for i in range(int(fraction * scipy.misc.comb(numCardsLeft, 2))):
            self.setFrac(handsSorted[i][0],1.0)

# Now that we have Range class, create functions to work with Ranges

def getEquityVsRange(hand, r, ea):
    """
    Input:
      hand - list of numbers
      r - Range object
      ea - Equity Array object
    """
    herocard1, herocard2 = hand
    eqs = ea.eArray[herocard1, herocard2, :, :] # Equity of all hands vs hero hands.  ea is an Equity Array of numCards x numCards x numCards x numCards.
    # r.r                 # numCards x numCards
    villRange = numpy.copy(r.r)
    zeroHandsWithConflicts(villRange, hand + ea.board)
    return sum(numpy.multiply(eqs, villRange)) / sum(villRange) # np.multiply is pairwise multiplication, not matrix

def plotEqDistn(r1, r2, board):
    """ Plot equity distributions of r1 vs r2 on board """
    xs = []
    ys = []
    handCount = 0.0
    for hand in r1.getHandsSortedAndEquities(r2, board):
        # plot hand at (handCount, equity) and (handCount + r1.getFrac(hand[0]), equity)
        xs.append(handCount)
        handCount += r1.getFrac(hand[0])
        xs.append(handCount)
        ys.append(hand[1])
        ys.append(hand[1])
    return xs, ys

def updateRange(r1, r2, n):
    """
    Input:
     r1 and r2 - Ranges
     n - positive integer
    Output: N/A
    Side-effect:
      Modifies r1 to incorporate some amount of r2.  In particular, the fraction of every hand in r1 at
      the end of the function will be (old amount) * (fraction) + (new amount) * (1-fraction)
      where fraction becomes closer to 1 the higher n is.
    """
    fraction = 1 - 1 / (n + 2.0) # Better if the fraction here is never exactly 0 or exactly 1
    for i in range(numCards):
        for j in range(i+1, numCards):
            hand = [i, j]
            r1.setFrac(hand, (r1.getFrac(hand)) * (fraction) + (r2.getFrac(hand)) * (1-fraction))

def doShoveFoldGame():
    """
    Solving the shove/fold:
    SB can either shove or fold at his first decision
    SB's strategy is defined by his jamming range, and the BB's by his calling range

    Fictitious play

    Input: N/A
    Outputs: N/A
    Side-effects: display SB shoving range and BB calling range
    """
    nIter = 200 # Number of iterations
    S = 10 # stack size in BBs
    ea = EquityArray(pe_string2card(['__','__','__','__','__']))

    # guess some initial ranges
    sbJamRange = Range()
    sbJamRange.setAllFracs(0.5)
    bbCallRange = Range()
    bbCallRange.setAllFracs(0.5)

    for n in range(nIter):
        # solve for the SB max expl strat
        bestSBJamRange = Range()
        for i in range(numCards):
            for j in range(i+1, numCards):
                hand = [i,j]
                bb_call_freq = bbCallRange.getNumHandsWithoutConflicts(hand) / numVillainHands
                equity = getEquityVsRange(hand, bbCallRange, ea)
                evJam = (1 - bb_call_freq) * (S+1) + (bb_call_freq) * equity * 2*S
                evFold = S - 0.5
                if (evJam > evFold):
                    bestSBJamRange.setFrac(hand, 1)
                else:
                    bestSBJamRange.setFrac(hand, 0)

        # update the SB strategy
        updateRange(sbJamRange, bestSBJamRange, n)

        # solve for BB max expl strat
        bestBBCallRange = Range()
        for i in range(numCards):
            for j in range(i+1, numCards):
                hand = [i, j]
                equity = getEquityVsRange(hand, sbJamRange, ea)
                evCall = 2 * S * equity
                evFold = S - 1
                if (evCall > evFold):
                    bestBBCallRange.setFrac(hand, 1)
                else:
                    bestBBCallRange.setFrac(hand, 0)
        # update BB strat
        updateRange(bbCallRange, bestBBCallRange, n)

### Set up Classes for Decision Points and Decision Tree ###

class DecPt:
    """
    A decision point will hold:
    player: a string describing whose decision point it is
            one of: "SB", "BB", "Nature", or "Leaf"
    initial_sb_cip: SB chip in pot before any decision is made at this point
    initial_bb_cip: similar
    eArray: an EquitiesArray describing the current board
    parentAction: a string describing the action that got us to this point
                  one of: "bet", "fold", "check", "call", or board cards
    newCardFreq:  only used if parentAction was new cards being dealt, and we
                  don't want all new cards to have equal probability of falling
    """
    def __init__(self, player, initial_sb_cip, initial_bb_cip, eArray, parentAction, newCardFreq = 1.0):
        self.player = player
        self.initial_sb_cip = initial_sb_cip
        self.initial_bb_cip = initial_bb_cip
        self.eArray = eArray
        self.parentAction = parentAction
        self.newCardFreq = newCardFreq

    def getPlayerCIP(self, player):
        """
        Input: player: string that is either "SB" or "BB"
        Output: chips in pot of player at beginning of decision point
        """
        if (player == "SB"):
            return self.initial_sb_cip
        elif (player == "BB"):
            return self.initial_bb_cip
        else:
            print "ERROR: DecPt.getPlayerCIP given player: " + player

class Tree:
    """
    A simple approach to a tree structure:
    Put all our decision points in a list (this implicitly numbers them):
       decPts
    Then, we need to keep track of parent and child relationship -- use a couple other arrays to do that
      parents: the i^th element of this array contain the number of the point which is the i^th point's parent
      children: the i^th entry in this list contain a list of the numbers of points which are the i^th
                point's children.  And if we want to know point i's children, we can find a list of them in
                children[i]
    Example:
                0       1     2        3         4
    decPts: (pointA, pointB, pointC, pointD, pointE)
    children: [ [], [], [], [1, 2], [0, 3]]
    parents: [4, 3, 3, 4, None]
    When we make a new tree, we'll just give it effective stack S, and a first decision point (root)
    Later, we will add new decision points
    """
    def __init__(self, S, root):
        self.effStack = S
        self.decPts = []
        self.children = []
        self.parents = []
        self.addDecPt(root, None)

    def getNumPoints(self):
        """
        Inputs: N/A
        Outputs: number of decision points in the tree
        Side-effects: N/A
        """
        return len(self.decPts)

    def getEffStack():
        """
        Inputs: N/A
        Outputs: Effective stack at the beginning of the decision tree
                 (corresponds to beginning of the hand, i.e. the case when players' CIP is 0)
        Side-effects: N/A
        """
        return self.effStack

    def addDecPt(self, point, parent):
        """
        Adds a new decision point to the tree
        Inputs:
            point: the new point (not previously in the tree)
            parent: a decision point already in the tree
        Outputs: N/A
        Side-effects: Adds a new decision point to the tree
        """
        self.decPts.append(point)
        self.children.append([])
        if (parent == None): # this should only be true for the root node
            self.parents.append(None) # Is this line needed?
        else:
            parentIndex = self.decPts.index(parent)
            self.children[parentIndex].append(self.getNumPoints() - 1)
            self.parents.append(parentIndex)

    def _repr_png_(self):
        """
        Inputs: N/A
        Outputs: returns a PNG file displaying the tree
        Side-effects: N/A
        """
        g = pydot.Dot(graph_type="digraph")
        for i in range(self.getNumPoints()):
            node_label = str(i) + ': ' + self.decPts[i].player \
                         + ' (' + str(self.decPts[i].initial_sb_cip) + ',' \
                         + str(self.decPts[i].initial_bb_cip) + ')'
            g.add_node(pydot.Node('node%d'%i, label=node_label))
        for i in range(self.getNumPoints()):
            for j in self.children[i]:
                g.add_edge(pydot.Edge('node%d'%i, 'node%d'%j, label=self.decPts[j].parentAction))
        return g.create(g.prog, 'png')

### Create Strategy Pair Class ###

class StrategyPair:
    """
    Strategy: a range for every action a player can take
    Strategy Pair is a pair of strategies -- one for each player
    So basically, a strategy pair will contain a range for every player action in the game.  Also, since
       there's an action for every decision point in the game (the point's parent action) (except the root)
       we can essentially keep track of all the range by associating one range with each decision point.
       (i.e. we'll number the ranges the same way we number decision points)
    So our StrategyPair class will:
      - hold a tree, called tree, and keep track of the tree's size
      - hold starting ranges for both players
      - hold a list of ranges, called ranges, such that range[i] is the range of hands that takes the
        parent action of the tree, decPts[i]
          - when we make a new strategy pair, we'll need to set these ranges intelligently
      - find the range that either player holds at any decision points
      - be able to display itself
      - be able to update itself (given a max exploitative strategy and a mixing fraction)
      - store the EVs of having any hand at any decision point for each player
        - there were will be two 3-D arrays, one for each player, of dimensions
               num-decision-points by numCards by numCards
            the first of those dimensions specifies a decision point, and the last two specify hole cards
            and the arrays hold the EVs of having that hand at that decision point
    Come up with a guess for starting ranges that is strategically reasonable?
    """
    def __init__(self, tree, sbStartingRange = None, bbStartingRange = None):
        self.tree = tree
        self.size = self.tree.getNumPoints()
        self.ranges = [Range() for i in range(self.size)]
        self.evs = dict()
        self.evs['SB'] = numpy.zeros((self.size, numCards, numCards))
        self.evs['BB'] = numpy.zeros((self.size, numCards, numCards))
        self.sbStartingRange = sbStartingRange
        if sbStartingRange == None:
            self.sbStartingRange = Range(1.0)
        self.bbStartingRange = bbStartingRange
        if bbStartingRange == None:
            self.bbStartingRange = Range(1.0)
        #  initialize the ranges
        self.initialize()

    def updateRanges(self, player, maxExplStrat, n):
        """
        Inputs:
         player: "SB" or "BB"
         maxExplStrat: a dict that maps decision point numbers to ranges for all of player's decision pts
         n: a positive integer (the iteration number)
        """
        for i in range(self.size):
            if (self.tree.decPts[i].player == player):
                for j in self.tree.children[i]:
                    updateRange(self.ranges[j], maxExplStrat[j], n)

    def getMostRecentRangeOf(self, player, iDecPt):
        """
        Inputs:
         player: "SB" or "BB"
         iDecPt: the number (index) of the decision point we're interested in
        Outputs: the range the player holds at the beginning of play at the decision point
        Side-effects: N/A
        """
        iCurrDecPt = iDecPt
        while (iCurrDecPt != 0 and self.tree.decPts[self.tree.parents[iCurrDecPt]].player != player):
            iCurrDecPt = self.tree.parents[iCurrDecPt]
        if iCurrDecPt == 0:  # we made it to the root
            return self.getStartingRangeOf(player)
        else:
            return self.ranges[iCurrDecPt]

    def getStartingRangeOf(self, player):
        """
        Inputs: player: "SB" or "BB"
        Outputs: the starting range of player
        Side-effects: N/A
        """
        if player == "SB":
            return self.sbStartingRange
        elif player == "BB":
            return self.bbStartingRange
        else:
            print "ERROR in StrategyPair.getStartingRangeOf: passed player: " + player
            return None

    def getRange(self, n):
        """
        Inputs: n: a number
        Outputs: the range associated with the parent action of a decision point n
        Side-effects: N/A
        """
        return self.range[n]

    def dump(self):
        """
        Inputs: N/A
        Outputs: N/A
        Side-effects: display all the ranges and actions in our tree and our solution
        """
        for i in range(1, self.size):
            parentActor = self.tree.decPts[self.tree.parents[i]].player
            action = self.tree.decPts[i].parentAction
            print str(i) + ": " + parentActor + " " + action
            if parentActor != "Nature":
                display(self.ranges[i])

    # Recursive approach to working on trees:
    # When we want to do something for every node in a tree, we can write a function f(),
    # does whatever we want for one node, and then calls itself on all the children of that node.
    # Then, to do the thing for all the nodes, we just call f() on the root node.

    def initialize(self):
        """
        Inputs: N/A
        Outputs: N/A
        Side-effects: sets all the ranges in the strategy pair, assuming the players start out with
                      their starting ranges and randomly (uniformly) select an action at each dec pt
        """
        self.initializeHelper(0, 1.0, 1.0)

    def initializeHelper(self, iCurrDecPt, sbScale, bbScale):
        """
        Inputs:
           iCurrDecPt: index of the current decision point
           sbScale and bbScale: numbers between 0 and 1 -- the fraction of the starting ranges that the
                                players bring to this decision point
        Outputs: N/A
        Side-effects: Set the range corresponding to the current decision point, and call itself
                      on all of the point's children (so as to do the right thing for them too)
        """
        children = self.tree.children[iCurrDecPt]
        numChildren = len(children)
        if self.tree.decPts[iCurrDecPt].player == 'SB':
            sbScale /= numChildren
            for iChild in children:
                self.ranges[iChild].r = self.sbStartingRange.r.copy()
                self.ranges[iChild].scaleFracs(sbScale)
                self.ranges[iChild].removeHandsWithConflicts(self.tree.decPts[iCurrDecPt].eArray.board)
        elif self.tree.decPts[iCurrDecPt].player == 'BB':
            bbScale /= numChildren
            for iChild in children:
                self.ranges[iChild].r = self.bbStartingRange.r.copy()
                self.ranges[iChild].scaleFracs(bbScale)
                self.ranges[iChild].removeHandsWithConflicts(self.tree.decPts[iCurrDecPt].eArray.board)
        for iChild in children:
            self.initializeHelper(iChild, sbScale, bbScale)

### Max Exploitative Strategy Functions ###

# Maximally exploitative strategies -- takes the highest-EV action with every hand in every spot
# Essentially, we'll fix Villain's strategy, and figure out how Hero should play every hand against it
# 1. Find the EV of taking every single action with every single hand (or, the EV of having every single holding in any spot,
#    assuming we play max exploitatively)
# 2. Build the max expl strategy
#
# How to find the EV at every decision point in the tree?  Agai , we're going to use a recursive traversal
#  of the tree.  Write a function that finds the EV at one decision point and have it call itself on the points children.
#  Of course this is also necessary because the EV at any decPt depends on the EVs of the children.
#
# Review Chapter 2
# So the right thing to do at any decision point is:
#  - recursively find the EVs of all the children
#  - if we're at a leaf, we capture our equity in the pot if we see a showdown, and if there was a fold, we
#    ship the pot to the right person
#  - if we're at Hero's decPt, Hero will make the most profitable choice at any hand (max EV over all choices with our hand)
#  - if we're at Villain's decPt, our EV is an average over our EVs after Villain makes each action, weighted
#    by how often he does that (card removal effects happen)
#  - if we're at Nature's decPt, our EV is an average over EVs that we get after each of the possible future cards (card removal)


def setMaxExplEVs(tree, strats, hero, villain):
    """
    Inputs:
      tree: a decision tree object
      strats: a StrategyPair
      hero: "SB" or "BB -- the player whose BB we're calculating
      villain: "SB" or "BB" -- the other guy
    Outputs: N/A
    Side-effects: set all the EVs in strats.evs[hero] to be the max expl EVs
    """
    setMaxExplEVsHelper(tree, 0, strats, hero, villain)

# Again, the idea here is to work recursively - define a "helper" function that:
#   - does the job for one decPt
#   - calls itself on all the decPt's children
# We do the job for every point in the tree by making one call to the helper starting at the root

def setMaxExplEVsHelper(tree, iDecPt, strats, hero, villain):
    """
    Inputs:
      tree: a decision tree object
      iDecPt: the index of a decision pointin the tree
      strats: a StrategyPair
      hero: "SB" or "BB -- the player whose BB we're calculating
      villain: "SB" or "BB" -- the other guy
    Outputs: N/A
    Side-effects: set all the EVs in strats.evs[hero] to be the max expl EVs
    """
    currDecPt = tree.decPts[iDecPt]
    if (currDecPt.player == 'Leaf'):
        setMaxExplEVsAtLeaf(tree, iDecPt, strats, hero, villain)
    elif (currDecPt.player == hero):
        setMaxExplEVsAtHeroDP(tree, iDecPt, strats, hero, villain)
    elif (currDecPt.player == villain):
        setMaxExplEVsAtVillainDP(tree, iDecPt, strats, hero, villain)
    else: # it must be the case that player is nature
        setMaxExplEVsAtNatureDP(tree, iDecPt, strats, hero, villain)

def setMaxExplEVsAtLeaf(tree, iDecPt, strats, hero, villain):
    """
    Signature is the same as for setMaxExplEVsHelper,
      but now we know the current decPt is a leaf
    """
    currDecPt = tree.decPts[iDecPt]
    if (currDecPt.parentAction == "fold"):
        if (tree.decPts[tree.parents[iDecPt]].player == hero): # Hero folded
            strats.evs[hero][iDecPt] = numpy.ones_like(strats.evs[hero][iDecPt])*(tree.effStack - currDecPt.getPlayerCIP(hero))
        else: #Villain folded
            strats.evs[hero][iDecPt] = numpy.ones_like(strats.evs[hero][iDecPt])*(tree.effStack + currDecPt.getPlayerCIP(villain))
    else: # we are seeing a showdown -- Hero's EV are all (S - (hero cip) + (hero cip + villain vip)*equity)
        for i in range(0, numCards):
            for j in range(i+1, numCards):
                strats.evs[hero][iDecPt][i][j] = (tree.effStack - currDecPt.getPlayerCIP(hero)) +\
                                                 (currDecPt.getPlayerCIP(hero)+currDecPt.getPlayerCIP(villain))*\
                                                  getEquityVsRange([i, j],strats.getMostRecentRangeOf(villain,iDecPt),currDecPt.eArray)
    setHandsWithConflicts(strats.evs[hero][iDecPt], currDecPt.eArray.board, -1)

def setMaxExplEVsAtHeroDP(tree, iDecPt, strats, hero, villain):
    """
    Signature is the same as for setMaxExplEVsHelper, but now we
      know the current decPt is Hero's
    """
    strats.evs[hero][iDecPt] = -1 * numpy.ones_like(strats.evs[hero][iDecPt])
    for iChild in tree.children[iDecPt]:
        setMaxExplEVsHelper(tree, iChild, strats, hero, villain)
        strats.evs[hero][iDecPt] = numpy.maximum(strats.evs[hero][iDecPt], strats.evs[hero][iChild])

def setMaxExplEVsAtVillainDP(tree, iDecPt, strats, hero, villain):
    """
    Signature is the same as for setMaxExplEVsHelper, but now we know the
    current decPt is Villian's or every hand, our EV is (how often Villain
    takes each action) * (our EV when he takes that action)
    """
    for iChild in tree.children[iDecPt]:
        setMaxExplEVsHelper(tree, iChild, strats, hero, villain)
    for i in range(0, numCards):
        for j in range(i+1, numCards):
            comboCounts = {}
            totalNumHandsinRange = 0
            for iChild in tree.children[iDecPt]:
                comboCounts[iChild] = strats.ranges[iChild].getNumHandsWithoutConflicts([i,j])
                totalNumHandsinRange += comboCounts[iChild]
            strats.evs[hero][iDecPt][i][j] = 0
            for iChild in tree.children[iDecPt]:
                strats.evs[hero][iDecPt][i][j] += strats.evs[hero][iChild][i][j] * (comboCounts[iChild] / totalNumHandsinRange)

# Signature is the same as for setMaxExplEVsHelper, but now we know the current decPt is Nature's
#
# Our EV for each hand is just over all future cards of: (likelihood of card) * (EV if that card comes)
# Card removal effects:
#   1. cards we hold can't come off
#   2. cards are less likely to come if they're in Villain's range
#
# Example of #2:
# Suppose we have 6-card deck: Qd, Jd, Td, 9d, 8d, 7d
# Hero holds 87dd, Villain's range is (JdTd, Jd9d)
# Suppose the board is empty, and we want to deal a new card.  How likely is any particular card to come?
# Well, 8d, 7d definitely can't come.
# Jd definitely can't come
# Td and 9d: Villain has blockers, so they're less likely
# Qd: this is the most likely card to come off
#
# When we say Villain's range is (JTdd, J9dd), what this means is that he would have played so as to
# get to this spot with both of those hands 100% of the time he's dealt them (and Hero and nature play
# appropriately) and he would have played this way never with any other hand.  Since he started the
# hand with the same amount of JT and J9, he must have each hand 50% of the time each.
# So, 50% of the time, he has J9dd, the new card is either Qd or the Td, with equal probability.
# The other 50%, he has JTdd, and the new card is Qd or 9d with equal probability.
# So the answer is: Qd comes 50% of the time, 9 and T comes 25% each, and no other cards can come.
#
# Other way to look at this: following events are the only possible ones, and they're all equally likely:
#   Villain has JT and new card is Q
#   Villain has JT and new card is 9
#   Villain has J9 and new card is Q
#   Villain has J9 and new card is T
#  4 possibilities -- 2 involve a Q being dealt, and 1 each involve the T and 9, so Q is dealt 2/4 times
#  and the T and 9 are each dealt 1/4 times
#  In the code:
#    for each possible new card (i.e. child of the current dec pt), look at how many hands in Villain's range
#    are compatible with it, comboCounts[iChild].  Also, keep track of total number of possibilities,
#    comboSum.  Then, the chance a particular card comes is just comboCounts[iChild] / comboSum.
#  NB: Note that this approach actually isn't quite right for spots where we artificially restrict the board cards that
#    can come off.  (In the second tree we looked at previously, we only used the 6s and 6d rivers), but it's close
#    and those trees are necessarily approximations anyway).

def setMaxExplEVsAtNatureDP(tree, iDecPt, strats, hero, villain):
    for iChild in tree.children[iDecPt]:
        setMaxExplEVsHelper(tree, iChild, strats, hero, villain)
    villainRange = strats.getMostRecentRangeOf(villain, iDecPt)
    for i in range(0, numCards):
        for j in range(i+1, numCards):
            if conflicts([i,j], tree.decPts[iDecPt].eArray.board):
                strats.evs[hero][iDecPt][i][j] = -1 # Mark -1 to indicate impossible situation
            else:
                comboCounts = {} # number of combos in Villain's range that don't conflict with the new card (or hero's hand)
                comboSum = 0.0   # sum of comboCounts for all the children
                for iChild in tree.children[iDecPt]:
                    newBoard = tree.decPts[iChild].eArray.board
                    if (conflicts(newBoard, [i,j])):
                        comboCounts[iChild] = 0
                    else:
                        comboCounts[iChild] = villainRange.getNumHandsWithoutConflicts([i,j]) * tree.decPts[iChild].newCardFreq
                    comboSum += comboCounts[iChild]
                strats.evs[hero][iDecPt][i][j] = 0
                if (comboSum == 0.0):
                    strats.evs[hero][iDecPt][i][j] = -1
                else:
                    for iChild in tree.children[iDecPt]:
                        strats.evs[hero][iDecPt][i][j] += strats.evs[hero][iChild][i][j] * (comboCounts[iChild] / comboSum)

### Fictitious Play Functions ###

def getAvgEV(strats, player, index):
    """
    Inputs:
      strats: a StrategyPair
      player: "SB" or "BB"
      index: the index or the number of an action (index is 0 at the top of the tree)
    Output: the average EV, over all hands, of player at index using strats
    """
    numCombos = 0.0
    summedEV = 0.0
    playerRange = strats.getMostRecentRangeOf(player, index)
    for i in range(numCards):
        for j in range(i+1, numCards):
            ev = strats.evs[player][index][i][j] # ev of hand ij at this point
            frac = playerRange.r[i][j] # fraction in range of hand ij at this point
            if ev >= 0:
                summedEV += ev * frac
                numCombos += frac
    return summedEV / numCombos

def doFP(tree, nIter, sbStartingRange = None, bbStartingRange = None):
    """
    Inputs:
      tree: a Tree that we are going to solve
      nIter: number of iterations to run for
      sbStartingRange and bbStartingRange: optional, Range objects
    """
    # initialize guess at strategies for both players
    strats = StrategyPair(tree, sbStartingRange, bbStartingRange)

    for i in range(1, nIter+1):
        print i

        setMaxExplEVs(tree, strats, "SB", "BB")
        sbMaxEVStrat = getMaxEVStrat(tree, "SB", strats)
        strats.updateRanges("SB", sbMaxEVStrat, i)
        print "SB average EV:" + str(getAvgEV(strats, 'SB', 0))

        setMaxExplEVs(tree, strats, "BB", "SB")
        bbMaxEVStrat = getMaxEVStrat(tree, "BB", strats)
        strats.updateRanges("BB", bbMaxEVStrat, i)
        print "BB average EV:" + str(getAvgEV(strats, 'BB', 0))

    return strats
