'''
Created on 8 Jul 2012

A grammar for XPath2 implemented using pyparsing.

This is dependent on the module 'tree', which contains the classes used to
build the parse hierarchy.

@author: James
'''

from pyparsing import *
from xpath2.parsetree import *

# Expressions: the top-level part of the recursion in the grammar.
singleExpr = Forward() 
expr = singleExpr + ZeroOrMore(Literal(',') + singleExpr)
parenthesizedExpr = Literal('(') + expr + Literal(')')

# Literals 
# TODO move these some where sensible - currently used by the path expressions.
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

# Function calls
functionCall = qName + Literal('(') + Optional(singleExpr + ZeroOrMore(Literal(',') + singleExpr)) + Literal(')')
functionCall.setParseAction(FunctionCall)

# Context item
contextItem = Literal('.')
contextItem.setParseAction(ContextItem)

primaryExpr = variableRef | literal | parenthesizedExpr | functionCall | contextItem


#
# Paths
#

# Predicates
predicate = Literal('[') + expr + Literal(']')
predicate.setParseAction(Predicate)

# Axis and steps
reverseAxis = oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") \
    + Literal("::")
forwardAxis = oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") \
    + Literal("::")

abrvParentStep = Literal('..')
abrvAttributeStep = Literal('@') + nodeTest
abrvChildStep = nodeTest.copy()

reverseStep = (reverseAxis + nodeTest) | abrvParentStep
forwardStep = (forwardAxis + nodeTest) | abrvAttributeStep | abrvChildStep

step = (forwardStep | reverseStep) + ZeroOrMore(predicate)
step.setParseAction(Step)

filterExpr = primaryExpr + ZeroOrMore(predicate)
stepExpr = filterExpr | step

# Paths
absolutePathStep = stepSeparator + stepExpr
relativePath = stepExpr + ZeroOrMore(absolutePathStep)
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

#
# Arithmetic
#

singleType = qName + Optional('?')
sequenceType = qName # FIXME and some other stuff...

signOp = oneOf('+ -')
castAsOp = Keyword('cast') + Keyword('as') + singleType
castableAsOp = Keyword('castable') + Keyword('as') + singleType
treatAsOp = Keyword('treat') + Keyword('as') + sequenceType
instanceOfOp = Keyword('instance') + Keyword('of')
intersectOp = Keyword('intersect') | Keyword('except')
unionOp = Keyword('union') | Literal('|')
multiOp = Literal('*') | Literal('div') | Literal('idiv') | Literal('mod')
addOp = Literal('+') | Literal('-')

#unaryExpr = operatorPrecedence(primaryExpr, [ # FIXME Should be 'pathExpr' not primaryExpr
#    (signOp, 1, opAssoc.RIGHT),
#    (castAsOp, 1, opAssoc.LEFT),
#   (castableAsOp, 1, opAssoc.LEFT),
#   (treatAsOp, 1, opAssoc.LEFT),
#    (instanceOfOp, 1, opAssoc.LEFT),
#    (intersectOp, 2, opAssoc.LEFT),
#   (unionOp, 2, opAssoc.LEFT),
#    (multiOp, 2, opAssoc.LEFT),
#    (addOp, 2, opAssoc.LEFT)
#    ])

unary = ZeroOrMore(signOp) + path
unary.setParseAction(unaryOpRightAssocHelper)
castAs = unary + Optional(castAsOp)
castAs.setParseAction(binaryOpLeftAssocHelper2)
castableAs = castAs + Optional(castableAsOp)
castableAs.setParseAction(binaryOpLeftAssocHelper2)
treatAs = castableAs + Optional(treatAsOp)
treatAs.setParseAction(binaryOpLeftAssocHelper2)
instanceOf = treatAs + Optional(instanceOfOp + sequenceType)
instanceOf.setParseAction(binaryOpLeftAssocHelper2)
intersect = instanceOf + ZeroOrMore(intersectOp + instanceOf)
intersect.setParseAction(binaryOpLeftAssocHelper)
union = intersect + ZeroOrMore(unionOp + intersect)
union.setParseAction(binaryOpLeftAssocHelper)
multi = union + ZeroOrMore(multiOp + union)
multi.setParseAction(binaryOpLeftAssocHelper)
add = multi + ZeroOrMore(addOp + multi)
add.setParseAction(binaryOpLeftAssocHelper)

#
# Other operators
#

# Sequence construction
rangeOp = Keyword('to')
range = add + Optional(rangeOp + add)
range.setParseAction(binaryOpLeftAssocHelper)

# Comparisons
valueCompOp = oneOf('eq ne lt le gt ge')
generalCompOp = oneOf('= != < <= > >=')
nodeCompOp = oneOf('is << >>')
comparison = range + Optional((valueCompOp | generalCompOp | nodeCompOp) + range)
comparison.setParseAction(binaryOpLeftAssocHelper)

# Logical
andExpr = comparison + ZeroOrMore(Keyword('and') + comparison)
andExpr.setParseAction(binaryOpLeftAssocHelper)
orExpr = andExpr + ZeroOrMore(Keyword('or') + andExpr)
orExpr.setParseAction(binaryOpLeftAssocHelper)

#
# If, quantified and for
#

ifExpr = Keyword('if') + Literal('(') + expr + Literal(')') + Keyword('then') + singleExpr \
    + Keyword('else') + singleExpr
ifExpr.setParseAction(IfExpr)
    
variableInExprList = variableRef + Keyword('in') + singleExpr \
    + ZeroOrMore(Literal(',') + variableRef + Keyword('in') + singleExpr)


forExpr = Keyword('for') + variableInExprList
forExpr.setParseAction(ForExpr)
    
quantified = (Keyword('some') | Keyword('every')) + variableInExprList + Keyword('satisfies') + singleExpr

#
# Top level recursive expression.
#
# TODO Make sure this is changed as we add more operators to the grammar
singleExpr << (forExpr | quantified | ifExpr | orExpr)
singleExpr.setParseAction(Expr)

# Grammar definition
Grammar = expr

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
