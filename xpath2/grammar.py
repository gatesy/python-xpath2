'''
Created on 8 Jul 2012

A grammar for XPath2 implemented using pyparsing.

This is dependent on the module 'tree', which contains the classes used to
build the parse hierarchy.

@author: James
'''

from pyparsing import *
from xpath2.parsetree import *
import unittest

# Expressions: the top-level part of the recursion in the grammar.
singleExpr = Forward() 
expr = singleExpr + ZeroOrMore(Literal(',') + singleExpr)
parenthesizedExpr = Literal('(') + expr + Literal(')')

# Literals
singleSlash = Literal("/")
doubleSlash = Literal("//")
stepSeparator = doubleSlash | singleSlash

# Names
ncName = Word(alphas + '_', alphanums + '.-')
qName = Optional(ncName + ':') + ncName
qName.setParseAction(QName)

wildcard = Literal("*") | (ncName + Literal(":*")) | (Literal("*:") + ncName)
wildcard.setParseAction(Wildcard)

# Test types
nameTest = qName | wildcard

anyKindTest = Literal('node') + Literal('(') + Literal(')')
anyKindTest.setParseAction(AnyKindTest)
textTest = Literal('text') + Literal('(') + Literal(')')
textTest.setParseAction(TextTest)
commentTest = Literal('comment') + Literal('(') + Literal(')')
commentTest.setParseAction(CommentTest)

# TODO need to sort all these out.
attributeTest = Literal('attribute') + Literal('(') + Optional(nameTest + Optional(Literal(",") + qName))

kindTest = anyKindTest | textTest | commentTest

nodeTest = nameTest | kindTest

#
# Primary expressions
#

# Literals
digits = Word(nums)

integerLiteral = digits.copy()
integerLiteral.setParseAction(IntegerLiteral)

decimalLiteral = (Literal ('.') + digits) | (digits + Literal('.') + Optional(digits))
decimalLiteral.setParseAction(DecimalLiteral)

doubleLiteral = (decimalLiteral | integerLiteral) + oneOf('e E') + Optional(oneOf('+ -')) + digits
doubleLiteral.setParseAction(DoubleLiteral)

escapedDblQuote = Literal('""')
escapedDblQuote.setParseAction(EscapedDblQuote)
escapedSglQuote = Literal("''")
escapedSglQuote.setParseAction(EscapedSglQuote)
stringLiteral = (Literal('"') + ZeroOrMore(escapedDblQuote | CharsNotIn('"')) + Literal('"')) \
    | (Literal("'") + ZeroOrMore(escapedSglQuote | CharsNotIn("'")) + Literal("'"))
stringLiteral.setParseAction(StringLiteral)

literal = stringLiteral | doubleLiteral | decimalLiteral | integerLiteral

# Variable references
variableRef = Literal('$') + qName
variableRef.setParseAction(VariableRef)

primaryExpr = variableRef | literal | parenthesizedExpr

# Arithmetic
#unaryExpr = Optional(oneOf('- +')) + primaryExpr # Should be a 'pathExpr' - use primary for now
singleType = qName + Optional('?')
sequenceType = qName # FIXME and some other stuff...

signOp = oneOf('+ -')
castAsOp = Keyword('cast') + Keyword('as') + singleType
castableAsOp = Keyword('castable') + Keyword('as') + singleType
treatAsOp = Keyword('treat') + Keyword('as') + sequenceType
instanceOfOp = Keyword('instance') + Keyword('of') + sequenceType
intersectOp = Keyword('intersect') | Keyword('except')
unionOp = Keyword('union') | Literal('|')
multiOp = Literal('*') | Literal('div') | Literal('idiv') | Literal('mod')
addOp = Literal('+') | Literal('-')

signOp.setParseAction(UnaryOp)
intersectOp.setParseAction(BinaryOp)
unionOp.setParseAction(BinaryOp)
multiOp.setParseAction(BinaryOp)
addOp.setParseAction(BinaryOp)

unaryExpr = operatorPrecedence(primaryExpr, [ # FIXME Should be 'pathExpr' not primaryExpr
    (signOp, 1, opAssoc.RIGHT),
    (castAsOp, 1, opAssoc.LEFT),
    (castableAsOp, 1, opAssoc.LEFT),
    (treatAsOp, 1, opAssoc.LEFT),
    (instanceOfOp, 1, opAssoc.LEFT),
    (intersectOp, 2, opAssoc.LEFT),
    (unionOp, 2, opAssoc.LEFT),
    (multiOp, 2, opAssoc.LEFT),
    (addOp, 2, opAssoc.LEFT)
    ])

# TODO add a 'binaryExpr' using operator precedence, since all unary ops have precedence over binary ops.

singleExpr << unaryExpr # FIXME This is wrong.

#
# Paths
#

# Predicates
predicate = Literal('[') + expr + Literal(']')

# Axis and steps
reverseAxis = oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") + "::"
forwardAxis = oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") + "::"

abrvParentStep = Literal('..')
abrvAttributeStep = Literal('@') + nodeTest
abrvChildStep = nodeTest.copy()

reverseStep = (reverseAxis + nodeTest) | abrvParentStep
forwardStep = (forwardAxis + nodeTest) | abrvAttributeStep | abrvChildStep

step = ((forwardStep | reverseStep) | primaryExpr) + ZeroOrMore(predicate)
step.setParseAction(Step)

# Paths
absolutePathStep = stepSeparator + step
relativePath = step + ZeroOrMore(absolutePathStep)
path = (Optional(stepSeparator) + relativePath) | singleSlash 

# Handle abbreviations
def handleAbrvParentStep(s, loc, tokens):
    return ['parent', '::', wildcard.parseString('*')[0]]


def handleAbrvAttributeStep(s, loc, tokens):
    return ['attribute', '::', tokens[1]]


def handleAbrvChildStep(s, loc, tokens):
    return ['child', '::', tokens[0]]

abrvParentStep.setParseAction(handleAbrvParentStep)
abrvAttributeStep.setParseAction(handleAbrvAttributeStep)
abrvChildStep.setParseAction(handleAbrvChildStep)

Grammar = path

def test(string, parser=qName):
    try:
        print (string)
        print (parser.parseString(string))
    except BaseException as err:
        print ('Error: ',err)
        
if __name__ == '__main__':
    pass
    #test('nodeN', step)
    #test('parent::nodeN', step)
    #test('self::a:*', step)
    #test('child::nodeN', step)
    #test('..', step)
    #test('@name', step)
    
    #test('A//B/@c', path)
    #test('/', path)
    #test('A/B', path)
    #test('/A/B', path)
    #test('A//C/parent::D', path)
