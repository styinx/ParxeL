from source.parxel.lexer import Lexer
from source.parxel.token import Token, TK
from unittest import TestCase


class LexerTest(TestCase):
    EMPTY_STRING = ''
    WHITESPACE_STRING = ' '
    SIMPLE_STRING = ' bli kla dub '
    COMPLEX_STRING = 'def func(self, name: str = "okay"): print(name) exit(1)'

    def assertEqualTokens(self, first: list[Token], second: list[TK]):
        self.assertEqual(list(map(lambda x: x.type, first)), second)

    def test___init__(self):
        # No arguments
        self.assertRaises(Lexer.EmptyStreamException, Lexer)

        # Empty string
        self.assertRaises(Lexer.EmptyStreamException, Lexer, LexerTest.EMPTY_STRING)

        # Whitespace string
        Lexer(stream=LexerTest.WHITESPACE_STRING)

        # Simple string
        Lexer(stream=LexerTest.SIMPLE_STRING)

        # Complex string
        Lexer(stream=LexerTest.COMPLEX_STRING)
    
    def test_tokenize(self):
        # Whitespace string
        lex = Lexer(stream=LexerTest.WHITESPACE_STRING)
        self.assertEqualTokens(lex.tokenize(), [TK.Space])

        # Simple string
        lex = Lexer(stream=LexerTest.SIMPLE_STRING)
        self.assertEqualTokens(lex.tokenize(), [TK.Space, TK.Word, TK.Space, TK.Word, TK.Space, TK.Word, TK.Space])

        # Complex string
        lex = Lexer(stream=LexerTest.COMPLEX_STRING)
        self.assertEqualTokens(lex.tokenize(), [
            TK.Word, TK.Space, TK.Word, TK.ParanthesisOpen, TK.Word, TK.Symbol, # def func(self,
            TK.Space, TK.Word, TK.Colon, TK.Space, TK.Word, TK.Space, TK.EqualSign, #  name: str =
            TK.Space, TK.QuotationMark, TK.Word, TK.QuotationMark, TK.ParanthesisClose, # "okay")
            TK.Colon, TK.Space, TK.Word, TK.ParanthesisOpen, TK.Word, TK.ParanthesisClose, # : print(name)
            TK.Space, TK.Word, TK.ParanthesisOpen, TK.Number, TK.ParanthesisClose # exit(1)
        ])

    def test_(self):
        # Whitespace string
        lex = Lexer(stream=LexerTest.WHITESPACE_STRING)

        # Simple string
        lex = Lexer(stream=LexerTest.SIMPLE_STRING)

        # Complex string
        lex = Lexer(stream=LexerTest.COMPLEX_STRING)
