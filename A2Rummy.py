# -*- coding: utf-8 -*-
"""
Created on Thu May 29 13:31:02 2014

@author: Seth King
"""
import pygame
from time import sleep
from PodSixNet.Connection import connection, ConnectionListener
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from operator import attrgetter

NOT_TURN = -1
DRAW_CARD = 1
SPREAD_DISCARD = 2

BG_COLOR = (0, 176, 0)
FG_COLOR = (255, 190, 0)


class Card():
    suitNames = ['Spades', 'Hearts', 'Clubs', 'Diamonds']
    faceNames = ['Ace', '2', '3', '4', '5', '6', '7', '8',
                 '9', '10', 'Jack', 'Queen', 'King']
    imagename = [['a', '2', '3', '4', '5', '6', '7', '8',
                  '9', 't', 'j', 'q', 'k'],
                 ['s', 'h', 'c', 'd']]

    def __init__(self, card_id):
        self.card_id = card_id
        if card_id == -1:
            self.card_image = pygame.image.load('./cards/null.gif')
        else:
            self.card_num, self.suit_num = divmod(card_id, 4)
            self.suit = Card.suitNames[self.suit_num]
            self.face = Card.faceNames[self.card_num]
            c = Card.imagename[0][self.card_num]
            v = Card.imagename[1][self.suit_num]
            imagefile = './cards/' + c + v + '.gif'
            self.card_image = pygame.image.load(imagefile)
            imagefile = './cards/inverted/inv_' + c + v + '.gif'
            self.card_inv_image = pygame.image.load(imagefile)
        self.rect = self.card_image.get_rect()
        self.selected = False

    def draw(self, surface, x, y):
        self.rect.x = x
        self.rect.y = y
        if self.selected:
            surface.blit(self.card_inv_image, (x, y))
        else:
            surface.blit(self.card_image, (x, y))

    def __str__(self):
        return "%s of %s" % (self.face, self.suit)

    def __eq__(self, oth):
        return (self.card_num, self.suit_num) == (oth.card_num, oth.suit_num)

    def __lt__(self, oth):
        return (self.card_num, self.suit_num) < (oth.card_num, oth.suit_num)


class Spread_area():
    def __init__(self, screen, x, y):
        self.surf = pygame.Surface((190, 150))
        self.surf.fill(BG_COLOR)
        self.rect = self.surf.get_rect()
        pygame.draw.rect(self.surf, FG_COLOR, self.rect, 6)
        self.cards = []
        self.filled = False
        self.screen = screen
        self.rect.x = x
        self.rect.y = y
        self.draw()

    def append(self, card):
        self.cards.append(card)
        return True

    def draw(self):
        dw = 15
        posistion = [20, 26]
        for i, c in enumerate(self.cards):
            c.selected = False
            c.draw(self.surf, *posistion)
            posistion[0] += dw
        self.screen.blit(self.surf, (self.rect.x, self.rect.y))


class Client(ConnectionListener):
    def __init__(self, host, port):
        pygame.init()
        width, height = 600, 550
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(BG_COLOR)
        pygame.display.set_caption("Acey-Deucey Rummy")
        self.clock = pygame.time.Clock()
        pygame.display.flip()
        self.deck_img = pygame.image.load('./cards/b.gif')
        self.deck_rect = self.deck_img.get_rect()

        self.Connect((host, port))
        self.hand = []
        self.discard = []
        self.spreads = [0] * 6

        self.selected = []

        self.turn = -1
        self.id = 99

        self.spreads[0] = Spread_area(self.screen, 10, 115)
        self.spreads[1] = Spread_area(self.screen, 205, 115)
        self.spreads[2] = Spread_area(self.screen, 400, 115)
        self.spreads[3] = Spread_area(self.screen, 10, 275)
        self.spreads[4] = Spread_area(self.screen, 205, 275)
        self.spreads[5] = Spread_area(self.screen, 400, 275)

        self.turn_text = 'Waiting for'
        self.mode_text = 'other player'
        self.wilds_text = ''
        pygame.font.init()
        self.font = pygame.font.Font('FreeSans.ttf', 24)
        self.faceNames = ['Ace', '2', '3', '4', '5', '6', '7', '8',
                          '9', '10', 'Jack', 'Queen', 'King']

    def Loop(self):
        for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                #if self.turn == self.id:
                #if self.mode != NOT_TURN
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == SPREAD_DISCARD:
                        for c in self.hand:
                            if c.rect.collidepoint(*event.pos):
                                print c
                                if c.selected:
                                    self.selected.remove(c)
                                else:
                                    self.selected.append(c)
                                c.selected = not(c.selected)
                        for s in self.spreads:
                            if s.rect.collidepoint(*event.pos):
                                if self.check_spread(self.selected):
                                    sp = []
                                    for c in self.selected:
                                        s.append(c)
                                        self.hand.remove(c)
                                        sp.append(c.card_id)
                                    s.filled = True
                                    self.selected = []
                                    data = {'action': 'new_spread',
                                            'spread': sp,
                                            'pid': self.id,
                                            'gameid': self.gameid}
                                    self.Send(data)
                                else:
                                    print 'no spread'
                        if (self.discard and
                           (self.discard.rect.collidepoint(*event.pos) and
                            len(self.selected) == 1)):
                            card = self.selected[0]
                            discard_id = card.card_id
                            self.hand.remove(card)
                            if self.hand == []:
                                data = {'action': 'end_hand',
                                        'pid': self.id,
                                        'gameid': self.gameid}
                            else:
                                self.selected = []
                                data = {'action': 'discard_endturn',
                                        'card': discard_id,
                                        'pid': self.id,
                                        'gameid': self.gameid}
                            self.Send(data)
                    if self.mode == DRAW_CARD:
                        if self.deck_rect.collidepoint(*event.pos):
                            print 'Draw from deck'
                            data = {'action': 'draw_card',
                                    'gameid': self.gameid,
                                    'pid': self.id}
                            self.Send(data)
                            self.mode_text = 'Spread or Discard'
                        if self.discard.rect.collidepoint(*event.pos):
                            print 'Draw from discard pile'
                            self.hand.append(self.discard)
                            self.hand.sort()
                            self.mode_text = 'Spread or Discard'
                            self.mode = SPREAD_DISCARD
                            self.Send({'action': 'discard_draw',
                                       'gameid': self.gameid})
        self.screen.fill(BG_COLOR)
        for s in self.spreads:
            s.draw()

        self.fsurf = self.font.render(self.turn_text, 1, FG_COLOR,
                                      BG_COLOR)
        self.screen.blit(self.fsurf, (10, 10))
        self.msurf = self.font.render(self.mode_text, 1, FG_COLOR,
                                      BG_COLOR)
        self.screen.blit(self.msurf, (10, 40))
        self.wsurf = self.font.render(self.wilds_text, 1, FG_COLOR,
                                      BG_COLOR)
        self.screen.blit(self.wsurf, (410, 10))

        self.draw_hand()
        connection.Pump()
        self.Pump()

    def check_spread(self, spread):
        spread.sort(key=attrgetter('card_num', 'suit_num'))
        for c in spread:
            print c
        if len(spread) < 3:
            return False
        torf = True
        last = ''
        #check num spread
        for c in spread:
            if c.card_num not in self.wilds:
                if last:
                    if c.card_num != last:
                        torf = False
                        break
                else:
                    last = c.card_num
        if not(torf):
            nwilds = 0
            last = ''
            ls = ''
            for c in spread:
                if c.card_num in self.wilds:
                    nwilds += 1
            for c in spread:
                if c.card_num not in self.wilds:
                    if last:
                        print c.card_num, last + 1, c
                        #print c.suit_num, ls, c
                        torf = (c.card_num == last + 1 and
                                c.suit_num == ls)
                        last = c.card_num
                        if not(torf):
                            if nwilds > 0:
                                nwilds -= 1
                                last += 1
                                torf = True
                            else:
                                break
                    else:
                        last = c.card_num
                        ls = c.suit_num
        return torf

    def start_turn(self):
        ch = raw_input('Choose:\n1 take discard\n' +
                       '2 Draw\n')

        if ch == '1':
            self.hand.append(self.discard)
            self.hand.sort()
            self.spread_discard()
        elif ch == '2':
            data = {'action': 'draw_card',
                    'gameid': self.gameid,
                    'pid': self.id}
            self.Send(data)
        else:
            self.take_turn()

    def spread_discard(self):
        ch = raw_input('Choose:\n1 Make Spread\n' +
                       '2 Add to existing spread\n' +
                       '3 Discard and Finish turn\n')
        if ch == '1':
            self.make_spread()
        elif ch == '2':
            print 'implement 2'
        elif ch == '3':
            if self.hand == []:
                data = {'action': 'end_hand',
                        'pid': self.id,
                        'gameid': self.gameid}
            else:
                print 'Choose card to discard:'
                for i, c in enumerate(self.hand):
                    print i, c
                card = raw_input('')
                discard_id = self.hand.pop(int(card)).card_id
                if self.hand == []:
                    data = {'action': 'end_hand',
                            'pid': self.id,
                            'gameid': self.gameid}
                else:
                    data = {'action': 'discard_endturn',
                            'card': discard_id,
                            'pid': self.id,
                            'gameid': self.gameid}
            self.Send(data)
        else:
            self.spread_discard()

    def make_spread(self):
        for i, c in enumerate(self.hand):
            print i, c
        cards = raw_input('Input card numbers for spread seperated by commas')
        print cards.split(',')
        cards = [int(i) for i in cards.split(',')]
        print cards
        print [c for c in cards]
        spread = [self.hand[c] for c in cards]
        spreadtf = self.check_spread(spread)
        if spreadtf:
            print 'Spread'
            sp = []
            for c in spread:
                self.hand.remove(c)
                sp.append(c.card_id)
            self.hand.sort()
            data = {'action': 'new_spread',
                    'spread': sp,
                    'pid': self.id,
                    'gameid': self.gameid}
            self.Send(data)
        else:
            print 'You suck'
            self.spread_discard()

    def draw_hand(self):
        pygame.draw.line(self.screen, FG_COLOR,
                         (0, 443), (600, 443), 4)
        self.hand.sort()
        cw = 73
        nc = len(self.hand)
        sp = 300 - nc*cw/2
        for i, c in enumerate(self.hand):
            c.draw(self.screen, sp + i*cw, 450)
        if self.discard:
            self.discard.draw(self.screen, 302, 5)
        self.draw_deck()
        pygame.display.flip()

    def draw_deck(self):
        self.screen.blit(self.deck_img, (225, 5))
        self.deck_rect.x = 225
        self.deck_rect.y = 5

    def Network_deal(self, data):
        print data
        h = data['hand']
        for c in h:
            card = Card(c)
            self.hand.append(card)

    def Network_discard_update(self, data):
        self.discard = Card(data['discard'])
        self.turn = data['turn']
        print 'Discard pile: ', self.discard
        self.draw_hand()
        self.selected = []
        if self.turn == self.id:
            self.mode = DRAW_CARD
            self.turn_text = 'Your turn'
            self.mode_text = 'Draw a card'
        else:
            self.mode = NOT_TURN
            self.turn_text = 'Other players turn'
            self.mode_text = ''

    def Network_discard_pile(self, data):
        self.discard = Card(data['discard'])

    def Network_new_spread(self, data):
        self.turn = data['turn']
        ns = data['spreads']
        for s in self.spreads:
            if not(s.filled):
                break
        for c in ns:
            ca = Card(c)
            s.append(ca)
        s.filled = True
        #print 'Implement view spreads'

    def Network_new_card(self, data):
        self.hand.append(Card(data['card']))
        self.hand.sort()
        self.mode = SPREAD_DISCARD

    def Network_score_hand(self, data):
        score = 0
        for c in self.hand:
            score += c.card_num
        data = {'action': 'gather_scores',
                'score': score,
                'pid': self.id,
                'gameid': self.gameid}
        self.Send(data)
        self.hand = []

    def Network_startgame(self, data):
        self.id = data['player']
        self.gameid = data['gameid']
        self.wilds = data['wilds']
        self.wilds_text = self.faceNames[self.wilds[0]] + "'s are wild"

    def Network_message(self, data):
        print data['message']

    def Network(self, data):
        print '\nnetwork data:', data

    def Network_error(self, data):
        print data['error']

if __name__ == "__main__":
    #c = Client('98.236.97.36', 40810)
    c = Client('localhost', 8080)
    while True:
        c.Loop()
        sleep(0.001)
