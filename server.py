# -*- coding: utf-8 -*-
"""
Created on Wed May 28 18:15:49 2014

@author: Seth King
"""

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
#from Deck import Deck
from time import sleep
import random


class ClientChannel(Channel):
    def Network(self, data):
        print data

    def Network_draw_card(self, data):
        self._server.draw_card(data)

    def Network_discard_endturn(self, data):
        self._server.discard_endturn(data)

    def Network_new_spread(self, data):
        self._server.new_spread(data)

    def Network_end_hand(self, data):
        self._server.end_hand(data)

    def Network_gather_scores(self, data):
        self._server.gather_scores(data)

    def Network_discard_draw(self, data):
        self._server.discard_draw(data)

    def Close(self):
        pass
        #self._server.close(self.gameid)


class RummyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = None
        self.currentIndex = 0

    def Connected(self, channel, addr):
        print 'new connection:', channel
        if self.queue is None:
            self.currentIndex += 1
            channel.gameid = self.currentIndex
            self.queue = Game(self.currentIndex)
            self.queue.players.append(channel)
            self.queue.players[0].score = [0] * 13
        else:
            channel.gameid = self.currentIndex
            self.queue.players.append(channel)
            self.queue.players[1].score = [0] * 13
            self.queue.players[0].Send({"action": "startgame",
                                        "player": 0,
                                        "gameid": self.queue.gameid,
                                        'wilds': self.queue.wilds})
            self.queue.players[1].Send({"action": "startgame",
                                        "player": 1,
                                        "gameid": self.queue.gameid,
                                        'wilds': self.queue.wilds})
            self.queue.deal_hand()
            self.games.append(self.queue)
            self.queue = None

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

    def draw_card(self, data):
        gid = data['gameid']
        game = [a for a in self.games if a.gameid == gid]
        game = game[0]
        card = game.deck.pop()
        pid = data['pid']
        cdata = {'action': 'new_card', 'card': card}
        game.players[pid].Send(cdata)

    def discard_endturn(self, data):
        gid = data['gameid']
        game = [a for a in self.games if a.gameid == gid]
        game = game[0]
        game.discard.append(data['card'])
        game.turn = (game.turn + 1) % 2

        data = {'action': 'discard_update',
                'discard': game.discard[-1],
                'turn': game.turn}
        game.send_to_all(data)

    def new_spread(self, data):
        gid = data['gameid']
        game = [a for a in self.games if a.gameid == gid]
        game = game[0]
        game.spreads.append(data['spread'])
        pid = data['pid']
        pid = (pid + 1) % 2
        data = {'action': 'new_spread',
                'spreads': game.spreads[-1],
                'turn': game.turn}
        game.players[pid].Send(data)

    def end_hand(self, data):
        gid = data['gameid']
        game = [a for a in self.games if a.gameid == gid]
        game = game[0]
        data = {'action': 'score_hand'}
        game.send_to_all(data)
        game.nscores_rcvd = 0

    def gather_scores(self, data):
        gid = data['gameid']
        game = [a for a in self.games if a.gameid == gid]
        game = game[0]
        game.nscores_rcvd += 1
        player = data['pid']
        game.players[player].score[game.nhands] = data['score']
        print 'player ', player, ' got ', data['score']
        if game.nscores_rcvd == len(game.players):
            if game.nhands >= 13:
                print 'End Game!'
                print sum(game.players[0].score), ' to ', \
                    sum(game.players[1].score)
            game.nhands += 1
            game.wilds[0] += 1
            game.turn = game.nhands % 2
            game.deal_hand()

    def discard_draw(self, data):
        gid = data['gameid']
        game = [a for a in self.games if a.gameid == gid][0]
        game.discard.pop()
        if game.discard:
            c = game.discard[-1]
        else:
            c = -1
        data = {'action': 'discard_pile',
                'discard': c}
        game.send_to_all(data)


class Game:
    handSize = 7

    def __init__(self, gid):
        self.deck = range(52)
        random.shuffle(self.deck)
        self.players = []
        self.gameid = gid
        self.discard = []
        self.turn = 0
        self.spreads = []
        self.nhands = 0
        self.wilds = [0]

    def deal_hand(self):
        self.deck = range(52)
        random.shuffle(self.deck)
        for player in self.players:
            hand = []
            for i in xrange(self.handSize):
                hand.append(self.deck.pop())
            data = {"action": "deal", "hand": hand}
            player.Send(data)
        self.discard.append(self.deck.pop())
        data = {'action': 'discard_update',
                'discard': self.discard[-1],
                'turn': self.turn}
        self.send_to_all(data)

    def send_to_all(self, data):
        for player in self.players:
            player.Send(data)


if __name__ == '__main__':
    #game.deck.show()
    #server = RummyServer(('98.236.97.36','40810'))
    server = RummyServer(localaddr=('localhost', 8080))
    server.Launch()
