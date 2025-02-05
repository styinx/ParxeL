class TK:
    def __class_getitem__(klass, sym: str) -> int:
        for k, v in TK.__dict__.items():
            if v == sym:
                return TK.__dict__[k]
        return TK.Undefined

    Undefined = 0

    Whitespaces = \
        [LineFeed, CarriageReturn, Space, HorizontalTabulator, VerticalTabulator] = \
        ['\n', '\r', ' ', '\t', '\v']

    Symbols = [
        ExclamationMark, QuotationMark, NumberSign, ParanthesisOpen, ParanthesisClose,
        Asterisk, Minus, Period, Slash, Semicolon,
        EqualSign, SquareBracketOpen, Backslash, SquareBracketClose,
        Backtick, CurlyBracketOpen, VerticalBar, CurlyBracketClose
    ] = [
        '!', '"', '#', '(', ')',
        '*', '-', '.', '/', ';',
        '=', '[', '\\', ']',
        '`', '{', '|', '}'
    ]

    Symbol = 0xF0
    Number = 0xF1  # Numeric
    Word = 0xF2  # Alphanumeric


class Token:
    def __init__(self, beg: int = 0, end: int = 0, row: int = 0, col: int = 0, type: TK = TK.Undefined, text: str = ''):
        self.beg = beg
        self.end = end
        self.row = row
        self.col = col
        self.type = type
        self.text = text

    def __repr__(self):
        return f'{bytes(self.text, encoding="utf-8")}'
