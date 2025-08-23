from hashlib import md5
from networkx import Graph
from pathlib import Path
import re

from parxel.token import Token

class Node:
    RE_PATH = re.compile(r'(\*|\w+)(?:\[(\w+)\s*(=|!=|in|not in)\s*(.*?)\])?')

    def __init__(self, parent = None):
        self.parent: Node = parent
        self.children: list[Node] = []
        self.scope: Node = self

        if parent:
            parent.add(self)

    def type(self) -> str:
        return self.__class__.__name__

    def hash(self, *tweak: str):
        hash_string = ''
        hash_string += self.type()
        hash_string += ''.join(str(arg) for arg in tweak if arg is not None)
        hash_string += str(len(self.children))
        hash_string += ''.join(set(map(lambda x : x.type(), self.children)))

        for child in self.children:
            hash_string += child.hash()

        return md5(hash_string.encode('utf-8')).hexdigest()

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

    def find(self, node_type):
        for child in self.children:
            if isinstance(child, node_type):
                return child
        return None

    def find_all(self, node_type):
        matches = []
        for child in self.children:
            if isinstance(child, node_type):
                matches.append(child)
        return matches

    def find_nested(self, node_type):
        try:
            it = self.walk()
            while it:
                node = next(it)
                if isinstance(node, node_type):
                    return node

        except StopIteration:
            pass

        return None

    def find_all_nested(self, node_type):
        matches = []
        try:
            it = self.walk()
            while it:
                node = next(it)
                if isinstance(node, node_type):
                    matches.append(node)

        except StopIteration:
            pass

        return matches

    def find_path(self, path: str):
        def get_path_part(part: str):
            m = re.match(Node.RE_PATH, part)
            if not m:
                raise ValueError(f"Invalid path: {part}")
            return m.groups()  # (type, key, op, val)

        def matches_path(node: "Node", part: tuple) -> bool:
            node_type, key, op, val = part

            if node_type not in (node.type(), '*'):
                return False

            if key:
                if not hasattr(node, key):
                    return False

                value = eval(val)
                attr = getattr(node, key)

                match op:
                    case '=':
                        return attr == value
                    case '!=':
                        return attr != value
                    case 'in':
                        return attr in value
                    case 'not in':
                        return attr not in value

            return True

        parts = [get_path_part(p) for p in path.strip().split('/') if p]

        def recurse(node: Node, idx: int):
            if idx >= len(parts):
                return [node]
            result = []
            for child in node.children:
                if matches_path(child, parts[idx]):
                    result.extend(recurse(child, idx + 1))
            return result

        return recurse(self, 0)

    def dump(self, level: int = 0, recursive: bool = False, properties: bool = False) -> str:
        s = f'{" " * level}{self.__class__.__name__:20s}\n'
        if properties:
            for k, v in self.__dict__.items():
                if k[0] != '_' and k[1] != '_':
                    s += f'{" " * level}- {k:20s} {v}\n'
        if recursive:
            for c in self.children:
                s += c.dump(level + 1, recursive, properties)

        return s

    def walk(self):
        yield self

        for child in self.children:
            yield from child.walk()


class Folder(Node):
    def __init__(self, path: Path, parent: Node = None):
        Node.__init__(self, parent=parent)

        self.path: Path = path

    def hash(self, *tweak: str):
        return super().hash(str(self.path), tweak)


class Document(Node):
    def __init__(self, filepath: Path, parent: Node = None):
        Node.__init__(self, parent=parent)

        self.filepath: Path = filepath

    def hash(self, *tweak: str):
        return super().hash(str(self.filepath), tweak)


class LexicalNode(Node):
    def __init__(self, tokens: list[Token], parent: Node = None):
        Node.__init__(self, parent=parent)

        self.tokens: list[Token] = tokens

    def hash(self, *tweak: str):
        return super().hash(self.raw(), tweak)

    def raw(self) -> str:
        return ''.join(list(map(lambda x: x.text, self.tokens)))


class BinaryNode(Node):
    def __init__(self, blob: bytes, parent: Node = None):
        Node.__init__(self, parent=parent)

        self.bytes: bytes = blob

    def hash(self, *tweak: str):
        return super().hash(self.bytes, tweak)
