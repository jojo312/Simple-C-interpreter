
# PLY template of parser for baby object language.

"""
Here is the syntax that is parsed:

P : Program
CL : CommandList
C : Command
DL : DeclarationList
D : Declaration
T : TypeTemplate
EL : ExpressionList
E : Expression
L : LefthandSide
IL : IdentifierList
I : Variable
N : Numeral

P ::=  DL  CL

DL ::=  D;*

D ::=  int I = E  |  ob I = E  |  proc I ( IL ) : CL end 
    |  class I : T

T ::=  extend L with { DL }  |  { DL }  |  L

CL ::=  C;*
   that is, a sequence of zero or more commands, separated by  ;
   ( CL ::=  C  |  C ; CL  |  empty  )

C ::=  L = E  |  if E : CL1 else CL2 end  |  print E  |  L ( EL )

EL ::=  E,*
   that is, a sequence of zero or more expressions, separated by  ,
   ( EL ::=   E  |  E , EL  | empty  )

E ::=  N  |  ( E1 OP E2 )  |  L  |  new T  |  nil
  where  OP ::=  +  |  -

L ::=  I  |  L . I

N ::=  string of digits

IL ::=  I,*
   that is, a sequence of zero or more identifiers, separated by  ,
   ( IL ::=  I  |  I , IL  | empty  )

I ::=  strings of letters, not including keywords


The output operator trees are nested lists:

PTREE ::=  [DLIST, CLIST]

DLIST ::=  [ DTREE* ]
           where  DTREE*  means  zero or more DTREEs

DTREE ::=  ["int", ID, ETREE]  |  ["ob", ID, ETREE]  |  ["proc", ID, ILIST, CLIST]
        |  ["class", ID, TTREE]

TTREE ::= ["extend", LTREE, DLIST]  |  ["struct", DLIST]  |  ["call", LTREE]

CLIST ::=  [ CTREE* ]

CTREE ::=  ["=", LTREE, ETREE]  |  ["if", ETREE, CLIST, CLIST]
        |  ["print", LTREE]  |  ["call", LTREE, ELIST]

ELIST ::=   [ ETREE* ]

ETREE ::=  NUM  |  ["+", ETREE, ETREE] |  ["deref", LTREE]  
        |  ["new", TTREE]  |  "nil"

LTREE ::=  ID  |  ["dot", LTREE, ID]

NUM   ::=  a nonempty string of digits

ILIST ::= [ ID+ ]

ID    ::=  a nonempty string of letters
"""

from ply import *
import a234lex

tokens = a234lex.tokens

# set precedences of infix tokens like this:
#precedence = ( #('left', 'TIMES','DIVIDE'),  etc.


######################################################

# Grammar rules and their corresponding operator trees:

# P ::= DL CL
# PTREE ::= DLIST CLIST
def p_Program(p):
    '''Program : DeclarationList CommandList''' 
    p[0] = [p[1], p[2]]  # that is,  answerP = [answerDL, answerCL]


# DL ::= D;*  (that is,   DL ::=  D ; DL | empty   
# DLIST ::= [ DTREE* ]
def p_DeclarationList1(p):
    '''DeclarationList : Declaration ';' DeclarationList'''
    p[0] = [p[1]] + p[3]

def p_DeclarationList2(p):
    '''DeclarationList : empty'''
    p[0] = []


# D ::=  int I = E  |  ob I = E  |  proc I ( IL ) : CL end |  class I : T
# DTREE ::=  ["int", ID]  |  ["ob", ID]  |  ["proc", ID, ILIST, CLIST]
#         |  ["class", ID, TTREE]
def p_Declaration1(p):
    '''Declaration : int ID '=' Expression '''
    p[0] = ["int", p[2], p[4]]

def p_Declaration2(p):
    '''Declaration : ob ID '=' Expression '''
    p[0] = ["ob", p[2], p[4]]

def p_Declaration3(p):
    '''Declaration : proc ID '(' IdentifierList ')' ':' CommandList end '''
    p[0] = ["proc", p[2], p[4], p[7]]

def p_Declaration4(p):
    '''Declaration : class ID ':' TypeTemplate '''
    p[0] = ["class", p[2], p[4]] 


# T ::=  extend L with { DL } | { DL } | L
# TTREE ::= ["extend", LTREE, DLIST ]  |  ["struct", DLIST]  |  ["call", LTREE]
def p_TypeTemplate1(p):
    '''TypeTemplate : extend LefthandSide with '{' DeclarationList '}' '''
    p[0] = ["extend", p[2], p[5]]

def p_TypeTemplate2(p):
    '''TypeTemplate : '{' DeclarationList '}' '''
    p[0] = ["struct", p[2]]

def p_TypeTemplate3(p):
    '''TypeTemplate : LefthandSide'''
    p[0] = ["call", p[1]]



# CL ::= C;*  (that is,   CL ::=  C | C ; CL | empty )
# CLIST ::= [ CTREE+ ]
def p_CommandList(p):
    '''CommandList : Command
                   | Command ';' CommandList
                   | empty '''
    if len(p) == 2 and p[1] != None :  # CommandList : Command
       p[0] = [p[1]]
    elif len(p) == 4 :  # CommandList :  Command ';' CommandList
       p[0] = [p[1]] + p[3]
    else :  # CommandList : empty,  because p[1] == None
       p[0] = []


# C ::=  L = E  |  if E : CL1 else CL2 end  |  print L  |  L ( EL )
#
# CTREE ::=  ["=", LTREE, ETREE]  |  ["if", ETREE, CLIST, CLIST]
#       |  ["print", LTREE]  |  ["call", LTREE, ELIST]
def p_Command1(c):
    '''Command : LefthandSide '=' Expression'''
    c[0] = ["=", c[1], c[3]]

def p_Command2(c):
    '''Command : if Expression ':' CommandList else CommandList end '''
    c[0] = ["if", c[2], c[4], c[6]]

def p_Command3(c):
    '''Command : print Expression'''
    c[0] = ["print", c[2]]

def p_Command4(c):
    '''Command : LefthandSide '(' ExpressionList ')' '''
    c[0] = ["call", c[1], c[3]]


# EL ::= E,*  (that is,   EL ::=  E ETAIL | empty   
#                         ETAIL ::=  , E ETAIL  |  empty    )
# ELIST ::= [ ETREE* ]
def p_ExpressionList1(t):
    '''ExpressionList : Expression EListTail'''
    t[0] = [t[1]] + t[2]

def p_ExpressionList2(t):
    '''ExpressionList : empty'''
    t[0] = []

def p_EListTail1(t):
    '''EListTail : ',' Expression EListTail'''
    t[0] = [t[2]] + t[3]

def p_EListTail2(t):
    '''EListTail : empty'''
    t[0] = []



# IL ::= I,*  (that is,   IL ::=  I ITAIL | empty   
#                         ITAIL ::=  , I ITAIL  |  empty    )
# ILIST ::= [ I* ]
def p_IdentifierList1(t):
    '''IdentifierList : ID IListTail'''
    t[0] = [t[1]] + t[2]

def p_IdentifierList2(t):
    '''IdentifierList :  empty'''
    t[0] = []

def p_IListTail1(t):
    '''IListTail : ',' ID IListTail'''
    t[0] = [t[2]] + t[3]

def p_IListTail2(t):
    '''IListTail : empty'''
    t[0] = []


# E ::=  N  |  ( E1 + E2 )  |  L  |  new T
# ETREE ::=  NUM  |  [OP, ETREE, ETREE] |  ["deref", LTREE]  
#         |  ["new", TTREE]  |  "nil"
# where
#        OP ::=  "+"  |  "-"

def p_Expression1(e):
    '''Expression : NUM'''
    e[0] = e[1]

def p_Expression2(e):
    '''Expression : '(' Expression Op Expression ')' '''
    e[0] = [e[3], e[2], e[4]]

def p_Expression3(e):
    '''Expression : LefthandSide '''
    e[0] = ["deref", e[1]]

def p_Expression4(e):
    '''Expression : new TypeTemplate '''
    e[0] = ["new", e[2]]

def p_Expression5(e):
    '''Expression : nil'''
    e[0] = "nil"


def p_op1(o):
    '''Op : '+' '''
    o[0] = "+"

def p_op2(o):
    '''Op : '-' '''
    o[0] = "-"


# L ::=  I  |  L . I 
# LTREE ::=  I  |  ["dot", LTREE, I]
def p_LefthandSide1(t):
    '''LefthandSide : ID'''
    t[0] = t[1]

def p_LefthandSide2(t):
    '''LefthandSide : LefthandSide '.' ID'''
    t[0] = ["dot", t[1], t[3]]



#### Generic empty construction --- no token at all
def p_empty(p):
    '''empty : '''
    pass   # retains  p[0] = None


#### Parse Error handler : prints location of error and quits parser
def p_error(p):
    print "SYNTAX ERROR at LexToken(grammar_phrase, input_word, line_number, char_number):"
    print (15 * " "), p
    print "PARSER QUITS."
    raise Exception

bparser = yacc.yacc()

def parse(data,debug=0):
    bparser.error = 0
    p = bparser.parse(data,debug=debug)
    if bparser.error: return None
    return p

