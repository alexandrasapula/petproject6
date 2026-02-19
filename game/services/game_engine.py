import random
from treys import Card, Evaluator


SUITS = ["H", "D", "C", "S"]
RANKS = ["2","3","4","5","6","7","8","9","T","J","Q","K","A"]


def create_deck():
    return [r+s for s in SUITS for r in RANKS]


def shuffle_deck(deck):
    random.shuffle(deck)


class Player:

    def __init__(self, user_id, username, seat):
        self.user_id = user_id
        self.username = username
        self.seat = seat

        self.cards = []
        self.chips = 1000

        self.folded = False
        self.allin = False
        self.bet = 0

    def reset_for_new_hand(self):
        self.cards = []
        self.folded = False
        self.allin = False
        self.bet = 0


class Game:

    SMALL = 5
    BIG = 10

    def __init__(self, players):
        self.players = sorted(players, key=lambda p: p.seat)
        self.table_cards = []
        self.pot = 0
        self.dealer_index = random.randrange(len(self.players))
        self.current_turn = 0
        self.stage = "preflop"
        self.deck = []
        self.start_hand()

    def start_hand(self):
        self.deck = create_deck()
        shuffle_deck(self.deck)
        self.table_cards = []
        self.pot = 0
        self.stage = "preflop"

        for p in self.players:
            p.reset_for_new_hand()
        self.assign_blinds()
        self.deal_cards()

    def assign_blinds(self):
        n = len(self.players)
        self.small_index = (self.dealer_index + 1) % n
        self.big_index = (self.dealer_index + 2) % n
        sb = self.players[self.small_index]
        bb = self.players[self.big_index]
        sb.bet = self.SMALL
        bb.bet = self.BIG
        sb.chips -= self.SMALL
        bb.chips -= self.BIG
        self.pot += self.SMALL + self.BIG
        self.current_turn = (self.big_index + 1) % n

    def one_left(self):
        alive = [p for p in self.players if not p.folded]
        return len(alive) == 1

    def betting_finished(self):
        active = [p for p in self.players if not p.folded and not p.allin]
        if len(active) <= 1:
            return True
        max_bet = max(p.bet for p in active)
        return all(p.bet == max_bet for p in active)

    def deal_cards(self):
        for _ in range(2):
            for p in self.players:
                p.cards.append(self.deck.pop())

    def get(self, uid):
        return next(p for p in self.players if p.user_id == uid)

    def next_player(self):
        n = len(self.players)
        for _ in range(n):
            self.current_turn = (self.current_turn + 1) % n
            p = self.players[self.current_turn]

            if not p.folded and not p.allin:
                return

    def finish_hand(self):
        evaluator = Evaluator()
        alive = [p for p in self.players if not p.folded]
        board = [Card.new(c) for c in self.community_cards]
        scores = [evaluator.evaluate(board, [Card.new(c) for c in p.cards]) for p in alive]
        min_score = min(scores)
        winners = [p for i, p in enumerate(alive) if scores[i] == min_score]
        share = self.pot // len(winners)
        for w in winners:
            w.chips += share
        self.pot = 0

    def fold(self, uid):
        self.get(uid).folded = True

    def call(self, uid):
        p = self.get(uid)
        needed = max(pl.bet for pl in self.players)
        diff = needed - p.bet
        diff = min(diff, p.chips)
        p.chips -= diff
        p.bet += diff
        self.pot += diff
        if p.chips == 0:
            p.allin = True

    def raise_bet(self, uid, amount):
        p = self.get(uid)
        amount = min(amount, p.chips)
        p.chips -= amount
        p.bet += amount
        self.pot += amount
        if p.chips == 0:
            p.allin = True

    def check(self, uid):
        pass

    def allin(self, uid):
        p = self.get(uid)
        self.pot += p.chips
        p.bet += p.chips
        p.chips = 0
        p.allin = True
    
    def after_action(self):
        if self.one_left():
            self.finish_hand()
            self.stage = "finished"
            return

        if self.betting_finished():
            for p in self.players:
                p.bet = 0
            self.advance_stage()
            if self.stage == "showdown":
                self.finish_hand()
                self.stage = "finished"
                return
            self.current_turn = (self.dealer_index + 1) % len(self.players)
            return
        self.next_player()


    def advance_stage(self):
        if self.stage == "preflop":
            self.stage = "flop"
            self.table_cards += [self.deck.pop() for _ in range(3)]
        elif self.stage == "flop":
            self.stage = "turn"
            self.table_cards.append(self.deck.pop())
        elif self.stage == "turn":
            self.stage = "river"
            self.table_cards.append(self.deck.pop())
        elif self.stage == "river":
            self.stage = "showdown"

    def get_state(self):

        return {
            "stage": self.stage,
            "pot": self.pot,
            "table": self.table_cards,
            "turn": self.players[self.current_turn].user_id,

            "players": [
                {
                    "id": p.user_id,
                    "name": p.username,
                    "chips": p.chips,
                    "bet": p.bet,
                    "folded": p.folded
                }
                for p in self.players
            ]
        }


class GameManager:

    def __init__(self):
        self.games = {}

    def create(self, room_id, players):
        self.games[room_id] = Game(players)
        return self.games[room_id].get_state()

    def handle(self, room_id, uid, msg):
        game = self.games[room_id]
        act = msg["action"]
        if act == "fold":
            game.fold(uid)
        elif act == "call":
            game.call(uid)
        elif act == "raise":
            game.raise_bet(uid, msg["amount"])
        elif act == "check":
            game.check(uid)
        elif act == "allin":
            game.allin(uid)
        game.after_action()
        return game.get_state()
