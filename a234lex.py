

# PLY template of scanner (lexical analyzer) for baby object language

from ply import *

# Define keywords:
keywords = ('if', 'else', 'while', 'end', 'print', 'new',
            'nil', 'int', 'ob', 'proc', 'class', 'extend', 'with')

# Define token names used in parse rules:
primitives = ('ID', 'NUM', 'NEWLINE')
tokens = keywords + primitives

# Define literal symbols used in parse rules:
literals = [';', ':', '=', '(', ')', '{', '}', '.', '+', '-', ',']

# Define tokens for primitive names to be recognized by parser:

t_ignore = ' \t\r'

def t_ID(t):   # defines an  ID  token or a keyword
    r'[A-Za-z][a-zA-Z0-9]*'
    if t.value in keywords:  # is token  t  a keyword?
        t.type = t.value
    return t
    
t_NUM = r'\d+'   # defines a  NUM token

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    #return t

# Error token:
def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

# initialize the lexical analyzer:
lexer = lex.lex(debug=0)


