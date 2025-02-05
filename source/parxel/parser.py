from io import FileIO, StringIO
from pathlib import Path
from parxel.token import Token, TK
from parxel.iterator import Iterator
from parxel.nodes import Node, Document
from parxel.lexer import Lexer


class Parser(Iterator):
    def __init__(self, tokens: list[Token] = None, root: Node = None, filename: str = None, filepath: Path = None, file: FileIO = None, stream: StringIO = None):

        if filename:
            filepath = Path(filename)

        if filepath:
            file = filepath.open('r')
        
        if file:
            stream = file.read()
        
        if not stream:
            raise Exception('No input')

        if not tokens:
            lexer = Lexer(filename=filename, filepath=filepath, file=file, stream=stream)
            tokens = lexer.tokenize()

        Iterator.__init__(self, iterable=tokens)

        if filepath:
            self.filepath: Path = filepath
            self.root = Document(filepath)
        else:
            self.root = Node()
        
        if root:
            self.root = root

        # Current Node
        self.nbeg: int = 0
        self.nend: int = 0

    def consume(self, type: TK) -> bool:
        if self.get() and self.get().type == type:
            self.next()
            return True
        return False

    def consume_strict(self, type: TK) -> None:
        if not self.consume(type):
            self.error(type)

    def consume_any(self, types: list[TK]) -> bool:
        if self.get() and self.get().type in types:
            self.next()
            return True
        return False

    def consume_until(self, type: TK) -> None:
        while self.get() and self.get().type != type:
            self.next()

    def consume_until_any(self, types: list[TK]) -> None:
        while self.get() and self.get().type not in types:
            self.next()

    def consume_while(self, type: TK) -> None:
        while self.get() and self.get().type == type:
            self.next()

    def consume_while_any(self, types: list[TK]) -> None:
        while self.get() and self.get().type in types:
            self.next()

    def discard(self) -> list[Token]:
        self.next()
        return self.collect_tokens()

    def number_of_tokens(self) -> int:
        return self.pos - self.nend

    def tokens(self) -> list[Token]:
        return self.buffer[self.nend:self.pos + 1]

    def collect_tokens(self) -> list[Token]:
        self.nbeg = self.nend  # End of last node
        self.nend = self.pos  # End of current node
        return self.buffer[self.nbeg:self.nend]

    def error(self, expected: TK) -> None:
        nl = '\n'
        t: Token = self.get()
        tokens = self.buffer[self.nend:self.pos + 1]
        text = "".join(list(map(lambda x: x.text, tokens)))
        indent = len(text[text.rfind(nl)]) if text.find(
            '\n') > -1 else len(text) - len(tokens[-1].text)

        msg = f'\n\n{self.filepath.absolute()}: Line {t.row} Col {t.col}\n\n'
        msg += f'{text}\n'
        msg += f'{indent * " "}{"^" * len(self.get().text)}\n\n'
        msg += f'Expected \'{expected}\' got \'{tokens[-1].text}\'\n'
        msg += f'Last tokens: {self.tokens()}\n'

        raise Exception(msg)

    def parse(self) -> Node | Document:
        raise NotImplementedError('Implement the "parse" method!')
