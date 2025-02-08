import re
import sys
from pathlib import Path
from parxel.nodes import Node, Document, LexicalNode
from parxel.token import Token, TK
from parxel.parser import Parser


# Markdown specific tokens
TK.TargetName = [TK.Number, TK.Word, TK.Period, TK.Slash, TK.Minus, TK.Colon]
TK.Text = [TK.Space, TK.HorizontalTabulator, TK.Symbol, TK.Number, TK.Word, TK.ParanthesisOpen,
           TK.ParanthesisClose, TK.Period, TK.Slash, TK.Minus, TK.QuotationMark, TK.Asterisk, TK.Colon]
TK.ReferenceText = [TK.Number, TK.Word] + TK.Whitespaces


# Markdown specific nodes
class Text(LexicalNode):
    def __init__(self, tokens: list, parent: Node = None):
        super().__init__(tokens, parent)

        self.text = self.raw().strip()


class Heading(Node):
    def __init__(self, parent: Node = None):
        super().__init__(parent)

        self.level = 1


class Image(LexicalNode):
    RE = re.compile(r'\!\[(.*)\]\((.*)\)')

    def __init__(self, tokens: list, parent: Node = None):
        super().__init__(tokens, parent)

        match = re.search(Image.RE, self.raw())

        self.text = match.group(1)
        self.target = match.group(2)


class Reference(LexicalNode):
    RE = re.compile(r'\[(.*)\]\((.*)\)')

    def __init__(self, tokens: list, parent: Node = None):
        super().__init__(tokens, parent)

        match = re.search(Reference.RE, self.raw())

        self.text = match.group(1)
        self.target = match.group(2)


class Code(LexicalNode):
    RE = re.compile('`([^`]*)`')

    def __init__(self, tokens: list, parent: Node = None):
        super().__init__(tokens, parent)

        match = re.search(Code.RE, self.raw())

        self.text = match.group(1)


class List(Node):
    def __init__(self, parent: Node = None):
        super().__init__(parent)


class ListItem(Node):
    def __init__(self, parent: Node = None):
        super().__init__(parent)


class Table(Node):
    class Align:
        left = 'left'
        center = 'center'
        right = 'right'

    def __init__(self, parent: Node = None):
        super().__init__(parent)

        self.columns = 0
        self.cell_alignment = []


class TableRow(Node):
    def __init__(self, parent: Node = None):
        super().__init__(parent)


class TableCell(Node):
    def __init__(self, parent: Node = None):
        super().__init__(parent)


class MD(Document, Parser):
    RE_ALGINMENT = re.compile('((:?-+:?)+)')

    class State:
        Start, \
            Heading, \
            List, \
            Table \
            = range(4)

    def __init__(self, filepath: Path):
        Document.__init__(self, filepath=filepath)
        Parser.__init__(self, root=self, filepath=filepath)

        self.state: list[MD.State] = [MD.State.Start]

    def parse(self):
        while self:
            self.parse_nodes()

        return self.root

    def parse_nodes(self):
        if self.state[-1] == MD.State.Start:

            if self.get().type == TK.NumberSign:
                self.parse_heading()
            elif self.get().type == TK.Minus:
                self.parse_list()
            elif self.get().type == TK.ExclamationMark:
                self.parse_image()
            elif self.get().type == TK.SquareBracketOpen:
                self.parse_reference()
            elif self.get().type == TK.Backtick:
                self.parse_code()
            elif self.get().type == TK.VerticalBar:
                self.parse_table()
            elif self.get().type in [TK.LineFeed, TK.Space]:
                self.discard()  # Discard newline or space at the start of a line
            elif self.get().type in TK.Text:
                self.parse_text()
            else:
                self.error(TK.Undefined)

        elif self.state[-1] == MD.State.Heading:
            if self.get().type == TK.SquareBracketOpen:
                self.parse_reference()
            elif self.get().type == TK.Backtick:
                self.parse_code()
            elif self.get().type in TK.Text:
                self.parse_text()
            elif self.get().type == TK.Space:
                self.discard()  # Discard space at the start of the line
            elif self.get().type == TK.LineFeed:
                return
            else:
                self.error(TK.Undefined)

        elif self.state[-1] == MD.State.List:
            if self.get().type == TK.SquareBracketOpen:
                self.parse_reference()
            elif self.get().type == TK.Backtick:
                self.parse_code()
            elif self.get().type == TK.Minus:
                self.parse_list()
            elif self.get().type == TK.Space:
                self.discard()  # Discard spaces at the start of the line
            elif self.get().type in TK.Text:
                self.parse_text()
            else:
                self.error(TK.Undefined)

        elif self.state[-1] == MD.State.Table:
            if self.get().type in TK.Text:
                self.parse_text()
            elif self.get().type == TK.ExclamationMark:
                self.parse_image()
            elif self.get().type == TK.SquareBracketOpen:
                self.parse_reference()
            elif self.get().type == TK.Backtick:
                self.parse_code()
            elif self.get().type == TK.VerticalBar:
                return
            else:
                self.error(TK.Undefined)

    def parse_text(self):
        self.consume_while_any(TK.Text)

        self.add_to_scope(Text(self.collect_tokens()))

    def parse_image(self):
        self.consume_strict(TK.ExclamationMark)

        self.consume_strict(TK.SquareBracketOpen)

        self.consume_while_any(TK.ReferenceText)

        self.consume_strict(TK.SquareBracketClose)

        self.consume_strict(TK.ParanthesisOpen)

        self.consume_while_any(TK.TargetName)

        self.consume_strict(TK.ParanthesisClose)

        self.add_to_scope(Image(self.collect_tokens()))

    def parse_reference(self):
        self.consume_strict(TK.SquareBracketOpen)

        self.consume_while_any(TK.ReferenceText)

        self.consume_strict(TK.SquareBracketClose)

        self.consume_strict(TK.ParanthesisOpen)

        self.consume_while_any(TK.TargetName)

        self.consume_strict(TK.ParanthesisClose)

        self.add_to_scope(Reference(self.collect_tokens()))

    def parse_code(self):
        is_block = False

        self.consume(TK.Backtick)

        if self.consume(TK.Backtick):
            self.consume_strict(TK.Backtick)

            is_block = True

        self.consume_until(TK.Backtick)

        self.next()

        if is_block:
            self.consume_strict(TK.Backtick)
            self.consume_strict(TK.Backtick)

        self.add_to_scope(Code(self.collect_tokens()))

    def parse_heading(self):
        self.state.append(MD.State.Heading)

        heading = Heading()
        self.enter_scope(heading)

        self.consume_while(TK.NumberSign)

        tokens = self.collect_tokens()
        heading.level = len(tokens)

        while self and self.get().type != TK.LineFeed:
            self.parse_nodes()

        self.exit_scope()
        self.state.pop()

    def parse_list(self):
        self.state.append(MD.State.List)

        list_root = List()
        self.enter_scope(list_root)

        while self and self.get().type != TK.LineFeed:
            self.parse_list_item()

            self.discard()  # Discard line feed

        self.exit_scope()
        self.state.pop()

    def parse_list_item(self):
        list_item = ListItem()
        self.enter_scope(list_item)

        self.discard()  # Discard list start

        while self and self.get().type != TK.LineFeed:
            self.parse_nodes()

        self.consume_until(TK.LineFeed)

        self.exit_scope()

    def parse_table(self):
        self.state.append(MD.State.Table)

        table = Table()
        self.enter_scope(table)

        while self and self.get().type != TK.LineFeed:
            self.parse_table_row()

            self.discard()  # Discard line feed

        if len(table.children) > 0:
            table.columns = len(table.children[0].children)

        if len(table.children) > 1:
            for cell in table.children[1].children:
                if len(cell.children) > 0 and hasattr(cell.children[0], 'text'):
                    text = cell.children[0].text
                    if re.search(r':-{3,}:', text):
                        table.cell_alignment.append(Table.Align.center)
                    elif text.find('---:') > -1:
                        table.cell_alignment.append(Table.Align.right)
                    else:
                        table.cell_alignment.append(Table.Align.left)

        if table.cell_alignment:
            table.children.pop(1)
        else:
            table.cell_alignment = [Table.Align.left] * table.columns

        self.exit_scope()

        self.state.pop()

    def parse_table_row(self):
        row = TableRow()
        self.enter_scope(row)

        self.discard()  # Discard row start

        while self and self.get().type != TK.LineFeed:
            self.parse_table_cell()

            self.discard()  # Discard cell separator or row end

        self.exit_scope()

    def parse_table_cell(self):
        cell = TableCell()
        self.add_to_scope(cell)

        while self and self.get().type != TK.VerticalBar:
            self.parse_nodes()

        self.exit_scope()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        if path.is_file():
            md = MD(filepath=path)
            node = md.parse()
        else:
            for file in path.rglob('*.md'):
                md = MD(filepath=file)
                node = md.parse()
    else:
        sys.exit(1)

    node.print(properties=True)
    node.print()

    sys.exit(0)
