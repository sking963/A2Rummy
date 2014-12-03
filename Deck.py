# -*- coding: utf-8 -*-
"""
Created on Mon May 26 00:29:20 2014

@author: Owner
"""
import random

deck = []


class Card():
    suitNames = ['Spades', 'Hearts', 'Clubs', 'Diamonds']
    faceNames = ['Ace', '2', '3', '4', '5', '6', '7', '8',
                 '9', '10', 'Jack', 'Queen', 'King']

    def __init__(self, suitNum=0, faceNum=0):
        self.suitNum = suitNum
        self.faceNum = faceNum

    def suitName(self):
        return Card.suitNames[self.suitNum]

    def faceName(self):
        return Card.faceNames[self.faceNum]

    def __str__(self):
        return "%s of %s" % (self.faceName(), self.suitName())


def showCards():
    suitNum = 0
    for suitNum in range(len(Card.suitNames)):
        for faceNum in range(len(Card.faceNames)):
            card = Card(suitNum, faceNum)
            deck.append(card)

    print 'Items in list are:\n\n'

    for item in deck:
        print "%d\t %s" % (deck.index(item)+1, item)


class Deck():
    def __init__(self):
        self.cards = []
        for suitNum in range(len(Card.suitNames)):
            for faceNum in range(len(Card.faceNames)):
                self.cards.append(Card(suitNum, faceNum))

    def show(self):
        print 'Items in list are:\n\n'
        for i in range(len(self.cards)):
            print "%d\t %s" % (i+1, self.cards[i])

    # your code here
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, count=1):
        rcards = []
        for i in xrange(count):
            rcards.append(self.cards.pop(0))
        return rcards


def check_combo_rank(hand):
    combo = (len(hand) >= 3)
    c1 = hand[0]
    for c in hand[1:]:
        if c1.faceNum != c.faceNum:
            combo = False
            break
    return combo


def check_combo_suit(hand):
    hand.sort(key=lambda h: (h.faceNum, h.suitNum))
    combo = (len(hand) >= 3)
    c1 = hand[0]
    lastnum = c1.faceNum
    for c in hand[1:]:
        cnum = c.faceNum
        if (c1.suitNum != c.suitNum) or (cnum != lastnum + 1):
            combo = False
            break
        lastnum = cnum
    return combo

if __name__ == '__main__':
    deck = Deck()
    deck.shuffle()
    deck.show()
    print '%s\n' % (deck.deal()[0])
    hand = deck.deal(count=7)
    hand.sort(key=lambda h: (h.faceNum, h.suitNum))
    #hand.sort(key=(attrgetter('faceNum', 'suitNum')))
    for c in hand:
        print '%s' % c
