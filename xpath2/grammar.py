'''
Created on 6 Jul 2012

@author: James
'''

from pyparsing import *

# Start by doing grammar for path expressions:

# First get the terminal names: QName and NCName
ncName = Word(alphas+"_", alphanums+"-.")
unprefixedName = ncName
prefixedName = ncName + ":" + ncName
qName = prefixedName | unprefixedName
wildcard = "*" | (ncName + ":" + "*") | ("*" + ":" + ncName)

# Expr is any expression
expr = Forward()

# PathExpr

# Terminals: /, // and axis
singleSlash = Literal("/")
doubleSlash = Literal("//")
reverseAxis = oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") + "::"
forwardAxis = oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") + "::"
openSq = Literal("[")
closeSq = Literal("]")

# First pass: ignore kind tests
#nodeTest = kindTest | nameTest
#nameTest = qName | wildcard

# Nodes are just QNames
nodeTest = qName | wildcard

# Predicates
predicateList = ZeroOrMore(openSq + expr + closeSq)

abbrevReverseStep = Literal("..")
reverseStep = (reverseAxis + nodeTest) | abbrevReverseStep

abbrevForwardStep = Optional("@") + nodeTest
forwardStep = (forwardAxis + nodeTest) | abbrevForwardStep

# First pass: ignore predicates
axisStep = (reverseStep | forwardStep) + predicateList

# First pass: ignore filter expressions
#stepExpr = filterExpr | axisStep
stepExpr = axisStep
relativePathExpr = stepExpr + ZeroOrMore((doubleSlash | singleSlash) + stepExpr)
absolutePathExpr = ((doubleSlash | singleSlash) + relativePathExpr)
pathExpr = absolutePathExpr | relativePathExpr

def test(strParam):
    try:
        print (strParam)
        print (pathExpr.parseString(strParam))
    except ParseException as err:
        print (err)
        
test("node")
test("parent::node")
test("node1/node2")
test("/node")
test("@attribute")
test("//a/b/c")
test("//node1/b/*//fg/@test")    
