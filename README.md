# ParxeL

A small lexer and parser utility library


## Install

[PyPi](https://pypi.org/project/parxel/0.0.1/)

`pip install parxel`


## Usage

```python
# Import lexer and tokens
from parxel.lexer import Lexer
from parxel.token import Token, TK

# Initialize via file name, path object, file object, or stream
lexer = Lexer(filename=filename, filepath=filepath, file=file, stream=stream)
# List of tokens depends on the defined token types defined in TK
tokens : list[Token] = lexer.tokenize()  # ['token', ' ', 'stream', ';', '...']

# Import parser
from parxel.parser import Parser

# Initialize via tokens, file name, path object, file object, or stream
parser = Parser(tokens=tokens, filename=filename, filepath=filepath, file=file, stream=stream)
parser.parse()  # has to be implemented by the concrete format

# Import nodes to represent the AST
from parxel.nodes import Document

# Sample from md.py
from md import MD

markdown = MD('README.md')
root : Document = markdown.parse()
```


## Sample

Calling:
`python -m md README.md`

Will produce the following AST:
```
MD
 Heading
  Text                bytearray(b' ParxeL')
 Text                bytearray(b'A small lexer and parser utility library')
 Heading
  Text                bytearray(b' Install')
 Reference           bytearray(b'[PyPi](https://pypi.org/project/parxel/0.0.1/)')
 Code                bytearray(b'`pip install parxel`')
 Heading
  Text                bytearray(b' Usage')
 Code                bytearray(b"```python\n# Import lexer and tokens\n [...] root : Document = markdown.parse()\n```")
```

The tokens of LexicalNode's should be processed.
In the above example the raw token stream of the `Text` b' Usage' will be stripped of whitespaces and stored in the `text` property.
Likewise the `Heading` node will contain the indentation level (1, 2, 3, ...) of the heading.
