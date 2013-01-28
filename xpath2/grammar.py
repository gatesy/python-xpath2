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

# Axis and steps
reverseAxis = oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") + "::"
forwardAxis = oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") + "::"

abrvParentStep = Literal('..')
abrvAttributeStep = Literal('@') + nodeTest
abrvChildStep = nodeTest.copy()

reverseStep = (reverseAxis + nodeTest) | abrvParentStep
forwardStep = (forwardAxis + nodeTest) | abrvAttributeStep | abrvChildStep

step = forwardStep | reverseStep
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

def test(string, parser=qName):
    try:
        print (string)
        print (parser.parseString(string))
    except BaseException as err:
        print ('Error: ',err)
        
if __name__ == '__main__':
    
    test('nodeN', step)
    test('parent::nodeN', step)
    test('self::a:*', step)
    test('child::nodeN', step)
    test('..', step)
    test('@name', step)
    
    #test('A//B/@c', path)
    #test('/', path)
    #test('A/B', path)
    #test('/A/B', path)
    #test('A//C/parent::D', path)
