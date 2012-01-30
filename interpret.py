
### INTERPRETER FOR OBJECT-ORIENTED LANGUAGE

"""The interpreter processes parse trees of this format:

PTREE ::=  DLIST CLIST
DLIST ::=  []
CLIST ::=  [ CTREE* ]
      where   CTREE*  means zero or more  CTREEs
CTREE ::=  ["=", LTREE, ETREE]  |  ["if", ETREE, CLIST, CLIST]
        |  ["print", ETREE]
ETREE ::=  NUM  |  [OP, ETREE, ETREE] |  ["deref", LTREE]
      where  OP ::= "+" | "-"
LTREE ::=  ID
NUM   ::=  a nonempty string of digits
ID    ::=  a nonempty string of letters


The interpreter computes the meaning of the parse tree, which is
a sequence of updates to heap storage.
"""

from heapmodule import *   # import the contents of the  heapmodule.py  module 


### INTERPRETER FUNCTIONS, one for each class of parse tree listed above.
#   See the end of program for the driver function,  interpretPTREE

def interpretDLIST(dlist) :
    """pre: dlist  is a list of declarations,  DLIST ::=  [ DTREE+ ]
       post:  memory  holds all the declarations in  dlist
    """
    for dec in dlist :
        interpretDTREE(dec)


def interpretDTREE(d) :
    """pre: d  is a declaration represented as a DTREE:
       DTREE ::= ["int", I, ETREE] | ["proc",I,ILIST,CLIST] | ["ob",I,ETREE]
                   | ["class",I,TTREE]
       post:  heap is updated with  d
    """
    decType = d[0]    
    handle, field = interpretLTREE(d[1])
    if not (handle == activeNS()):
        handle = activeNS()
    if decType == "int": # ["int", I, ETREE]
        rval = interpretETREE(d[2])
        declare(handle,field,rval)
    elif decType == "proc": # ["proc",I,ILIST,CLIST]
        rval = allocateClosure(handle,field,[decType,d[2],d[3],handle])
        declare(handle,field,rval)
    elif decType == "ob": # ["ob",I,ETREE]
        # Check to make sure ETREE is either a handle to an object or nil
        if (isinstance(d[2],str) and d[2] == "nil") or d[2][0] == "new":
            rval = interpretETREE(d[2])
            declare(handle,field,rval)
        else:
            crash(d,"invalid ob type")
    elif decType == "class": # ["class", I, T]
        rval = allocateClosure(handle,field,[decType,d[2],handle])
        declare(handle,field,rval)
    else: crash(d,"invalid declaration")


def interpretCLIST(clist) :
    """pre: clist  is a list of commands,  CLIST ::=  [ CTREE+ ]
                  where  CTREE+  means  one or more CTREEs
       post:  memory  holds all the updates commanded by program  p
    """
    for command in clist :
        interpretCTREE(command)


def interpretCTREE(c) :
    """pre: c  is a command represented as a CTREE:
       CTREE ::=  ["=", LTREE, ETREE]  |  ["if", ETREE, CLIST, CLIST2] 
        |  ["print", LTREE] | ["call",ID,ELIST]
       post:  heap  holds the updates commanded by  c
    """
    operator = c[0]
    if operator == "=" :   # , ["=", LTREE, ETREE]
        handle, field = interpretLTREE(c[1])
        rval = interpretETREE(c[2])
        store(handle, field, rval)
    elif operator == "print" :   # ["print", LTREE]
        print interpretETREE(c[1])
    elif operator == "if" :   # ["if", ETREE, CLIST1, CLIST2]
        test = interpretETREE(c[1])
        if test != 0 :
            interpretCLIST(c[2])
        else :
            interpretCLIST(c[3])
    elif operator == "call" : # ["call",ID,ELIST]
        handle, field = interpretLTREE(c[1])
        closure = lookupClosure(lookup(handle,field))
        if closure[0] == "proc":
            il = closure[1]
            cl = closure[2]
            newNS = allocateNS()
            store(newNS,"parentns",closure[3])
            el = c[2]
            if len(il) != len(el): # number of parameters don't match
                crash(field, "invalid number of parameters")
            for i,e in zip(il,el):
                declare(newNS,i,interpretETREE(e))
            pushNS(newNS)
            interpretCLIST(cl)
            popNS()
        else : crash(closure, "invalid procedure call")
    else :  crash(c, "invalid command")


def interpretETREE(etree) :
    """interpretETREE computes the meaning of an expression operator tree.
         ETREE ::=  NUM  |  [OP, ETREE, ETREE] |  ["deref", LTREE] | ["new",TTREE]
         OP ::= "+" | "-"
        post: updates the heap as needed and returns the  etree's value
    """
    if isinstance(etree, str) and etree.isdigit() :  # NUM
      ans = int(etree)
    elif isinstance(etree,str) and etree == "nil": # nil
        ans = "nil"
    elif  etree[0] in ("+", "-") :      # [OP, ETREE, ETREE]
        ans1 = interpretETREE(etree[1])
        ans2 = interpretETREE(etree[2])
        if isinstance(ans1,int) and isinstance(ans2, int) :
            if etree[0] == "+" :
                ans = ans1 + ans2
            elif etree[0] == "-" :
                ans = ans1 - ans2
        else : crash(etree, "addition error --- nonint value used")
    elif  etree[0] == "deref" :    # ["deref", LTREE]
        handle, field = interpretLTREE(etree[1])
        ans = lookup(handle,field)
    elif etree[0] == "new":     # ["new",TTREE]
        ans = interpretTTREE(etree[1])
    else :  crash(etree, "invalid expression form")
    return ans

def interpretTTREE(ttree):
    """interpretTTREE allocates a new namespace and pushes the namespace's
        handle on the activation stack
        TTREE ::= ["struct", DLIST] | ["call", LTREE]
        post: evaluates DLIST and pops the activation stack and returns the
        popped handle.
    """
    if ttree[0] == "struct":
        newNS = allocateNS()
        store(newNS,"parentns",activeNS())
        pushNS(newNS)
        interpretDLIST(ttree[1])
        ans = popNS()
    elif ttree[0] == "call":
        handle, field = interpretLTREE(ttree[1])
        closure = lookupClosure(lookup(handle,field))
        if closure[0] == "class":
            ans = interpretTTREE(closure[1])
        else:
            crash(ttree,"invalid call")
    else:
        crash(ttree, "invalid struct")
    return ans

def interpretLTREE(ltree) :
    """interpretLTREE computes the meaning of a lefthandside operator tree.
          LTREE ::=  ID | ["dot",LTREE,ID]
       post: returns a pair,  (handle,varname),  the L-value of  ltree
    """
    
    if isinstance(ltree, str) :  #  ID ?
        ans = (None,None)
        act = activeNS()
        par = lookup(act,"parentns")
        if isLValid(act,ltree): # look in the active namespace
            ans = (act, ltree)    # use the handle to the active namespace
        elif isLValid(par,ltree) and par != "nil":  # look in the parent namespace
            ans = (par,ltree)
        else: # not declared in either so use the active namespace
            ans = (act,ltree)
    elif ltree[0] == "dot" : # ltree has form, ["dot",LTREE,ID]
        lval = interpretLTREE(ltree[1])
        handle = lookup(lval[0],lval[1])
        ans = (handle, ltree[2])
    else :
        crash(ltree, "illegal L-value")
    return ans


def crash(tree, message) :
    """pre: tree is a parse tree,  and  message is a string
       post: tree and message are printed and interpreter stopped
    """
    print "Error evaluating tree:", tree
    print message
    print "Crash!"
    printHeap()
    raise Exception   # stops the interpreter


### MAIN FUNCTION

def interpretPTREE(tree) :
    """interprets a complete program tree
       pre: tree is a  PTREE ::= [ DLIST, CLIST ]
       post: heap holds all updates commanded by the  tree
    """
    initializeHeap()
    interpretDLIST(tree[0])
    interpretCLIST(tree[1])
    printHeap()

