from io import FileIO, StringIO
from pathlib import Path
from .token import Token, TK
from .iterator import Iterator


def is_alpha(c: str) -> bool:
    if c:
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_'
    return False

def is_numeric(c: str) -> bool:
    if c:
        return '0' <= c <= '9'
    return False

def is_alpha_numeric(c: str) -> bool:
    return is_alpha(c) or is_numeric(c)


class Lexer(Iterator):
    class EmptyStreamException(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    def __init__(self, filename: str = None, filepath: Path = None, file: FileIO = None, stream: StringIO = None):

        if filename:
            filepath = Path(filename)

        if filepath:
            file = filepath.open('r')
        
        if file:
            stream = file.read()
        
        if not stream:
            raise Lexer.EmptyStreamException('No input given to lexer!')

        Iterator.__init__(self, iterable=stream)

        self.tokens : list[Token] = []

        # File position
        self.row : int = 0
        self.col : int = 0

        # Current token
        self.tbeg : int = 0
        self.tend : int = 0

    def next(self) -> str:
        c = super().next()

        self.col += 1

        if c == TK.LineFeed:
            self.row += 1
            self.col = 0

        return c

    def make_token(self, type: int) -> Token:
        self.tbeg = self.tend  # End of last token
        self.tend = self.pos + 1  # End of current token
        text = self.buffer[self.tbeg:self.tend] if self.tend - self.tbeg > 1 else self.buffer[self.pos]
        return Token(self.tbeg, self.tend, self.row, self.col, type, text)

    def tokenize(self) -> list[Token]:
        c : str = self.get()

        while self and c:

            if c in TK.Whitespaces:
                self.tokens.append(self.make_token(TK[c]))

            elif c in TK.Symbols:
                self.tokens.append(self.make_token(TK[c]))

            elif is_numeric(c):
                while is_numeric(c):
                    c = self.next()
                self.prev()

                self.tokens.append(self.make_token(TK.Number))

            elif is_alpha(c):
                while is_alpha_numeric(c):
                    c = self.next()
                self.prev()
                
                self.tokens.append(self.make_token(TK.Word))

            else:
                self.tokens.append(self.make_token(TK.Symbol))
            
            c = self.next()

        return self.tokens
