from pathlib import Path
from parxel.token import Token


class Node:
    def __init__(self, parent=None):
        self.parent: Node = parent
        self.children: list[Node] = []
        self.scope: Node = self

    def type(self) -> str:
        return self.__class__.__name__

    def add(self, other) -> None:
        other.parent = self
        self.children.append(other)

    def enter_scope(self, other) -> None:
        self.scope.add(other)
        self.scope = other

    def exit_scope(self) -> None:
        self.scope = self.scope.parent

    def add_to_scope(self, other) -> None:
        self.scope.add(other)

    def print(self, level: int = 0, properties: bool = False) -> None:
        print(f'{" " * level}{self.__class__.__name__:20s}')
        if properties:
            for k, v in self.__dict__.items():
                if k[0] != '_' and k[1] != '_':
                    print(f'{" " * level}- {k:20s} {v}')
        for c in self.children:
            c.print(level + 1, properties)

    def walk(self):
        yield self

        for child in self.children:
            yield from child.walk()


class Folder(Node):
    def __init__(self, path: Path, parent: Node = None):
        Node.__init__(self, parent=parent)

        self.path: Path = path


class Document(Node):
    def __init__(self, filepath: Path, parent: Node = None):
        Node.__init__(self, parent=parent)

        self.filepath: Path = filepath


class LexicalNode(Node):
    def __init__(self, tokens: list[Token], parent: Node = None):
        Node.__init__(self, parent=parent)

        self.tokens: list[Token] = tokens

    def raw(self) -> str:
        return ''.join(list(map(lambda x: x.text, self.tokens)))

    def print(self, level: int = 0, properties: bool = False) -> None:
        print(
            f'{" " * level}{self.__class__.__name__:20s}{bytearray(self.raw(), encoding="utf-8")}')
        if properties:
            for k, v in self.__dict__.items():
                if k[0] != '_' and k[1] != '_':
                    print(f'{" " * level}- {k:20s} {v}')
        for c in self.children:
            c.print(level + 1, properties)
