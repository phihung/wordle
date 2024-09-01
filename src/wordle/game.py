from enum import Enum
from dataclasses import dataclass, field, asdict
import json
import random
from pathlib import Path


x = json.load((Path(__file__).parent / "dictionary.json").open())
VOCAB = set(w.upper() for w in x["valid"] + x["target"])
TARGETS = [w.upper() for w in x["target"]]

MAX_TRIES = 6
WORD_LEN = 5

Char = str


class State(str, Enum):
    WIN = "win"
    LOSE = "lose"
    PLAYING = "playing"


class Eval(str, Enum):
    CORRECT = "c"
    EXIST = "e"
    WRONG = "w"
    UNK = "_"
    EMPTY = "x"


@dataclass
class Game:
    target: str
    guess: list[Char] = field(default_factory=list)
    valid: list[Eval] = field(default_factory=list)
    current: list[Char] = field(default_factory=list)
    keyboard: list[Eval] = field(default_factory=lambda: ["_"] * 26)
    state: State = State.PLAYING

    @classmethod
    def from_str(self, data: str | None):
        if data is not None:
            try:
                return Game(**json.loads(data))
            except json.JSONDecodeError:
                pass
        return Game(random.choice(TARGETS))

    def to_str(self) -> str:
        return json.dumps(asdict(self))

    def get_keyboard_state(self, key):
        if len(key) == 1:
            return self.keyboard[ord(key) - ord("A")]
        return Eval.UNK

    def get_square_state(self, i):
        n = len(self.guess)
        if i < n:
            return self.guess[i], self.valid[i]

        if i < n + len(self.current):
            return self.current[i - n], Eval.UNK

        return "", Eval.EMPTY

    # Return updated squares and keys
    def keypress(self, key: str):
        keys = []
        if key == "ENTER":
            word = self.current
            squares = self._enter()
            keys = word if squares else []
        elif key == "DEL":
            squares = self._backspace()
        else:
            squares = self._add_char(key)
        return squares, keys

    def _add_char(self, c: str):
        ic = ord(c) - ord("A")
        if (
            self.state == State.PLAYING
            and len(self.current) < WORD_LEN
            and self.keyboard[ic] != Eval.WRONG
        ):
            self.current.append(c)
            return [len(self.guess) + len(self.current) - 1]
        return []

    def _backspace(self):
        if self.state == State.PLAYING and len(self.current) > 0:
            self.current = self.current[:-1]
            return [len(self.guess) + len(self.current)]
        return []

    def _enter(self):
        word = "".join(self.current)
        if self.state != State.PLAYING or len(self.current) != WORD_LEN or word not in VOCAB:
            return []

        self.guess += self.current
        for i, c in enumerate(self.current):
            v = (
                Eval.CORRECT
                if c == self.target[i]
                else Eval.EXIST
                if c in self.target
                else Eval.WRONG
            )
            self.valid.append(v)
            ic = ord(c) - ord("A")
            if self.keyboard[ic] != Eval.CORRECT:
                self.keyboard[ic] = v

        if word == self.target:
            self.state = State.WIN
        elif len(self.guess) == MAX_TRIES * WORD_LEN:
            self.state = State.LOSE
        self.current = []
        return [len(self.guess) - WORD_LEN + i for i in range(WORD_LEN)]
