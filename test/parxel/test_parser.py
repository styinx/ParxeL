from source.parxel.nodes import BinaryNode, LexicalNode
from source.parxel.parser import BinaryParser, Node, TextParser
from source.parxel.token import TK
from unittest import TestCase


class TextParserTest(TestCase):
    def test_grammar(self):

        TEST_STRING = str(
            'fun caller'
            'end'
            'fun another'
            'end'
        )

        class Fun(LexicalNode):
            def __init__(self, tokens, parent = None):
                super().__init__(tokens, parent)

        doc = Node()
        parser = TextParser(stream=TEST_STRING)

        while parser:
            parser.consume_strict(TK.Word)

            if parser.collect_tokens() != 'fun':
                parser.next()
                continue

            parser.consume_strict(TK.Word)
            name = parser.collect_tokens()

            parser.consume_strict(TK.Word)
            if parser.collect_tokens() != 'end':
                parser.next()
                continue

            fun = Fun(name)
            doc.add(fun)
        

class BinaryParserTest(TestCase):
    def test_blob(self):
        class LE(BinaryNode):
            def __init__(self, blob, parent = None):
                super().__init__(blob, parent)

                self.number = int.from_bytes(blob, 'little')

        class BE(BinaryNode):
            def __init__(self, blob, parent = None):
                super().__init__(blob, parent)

                self.number = int.from_bytes(blob, 'big')
        
        doc = Node()
        parser = BinaryParser(bytes=bytes('le1234be12be21le4321', encoding='utf-8'))

        while parser:
            parser.consumen(2)
            magic = parser.collect_bytes()

            if magic == b'le':
                parser.consumen(4)
                num = LE(parser.collect_bytes())
                doc.add(num)

            elif magic == b'be':
                parser.consumen(2)
                num = BE(parser.collect_bytes())
                doc.add(num)
