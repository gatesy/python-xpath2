'''
Created on 8 Jul 2012

A grammar for XPath2 implemented using pyparsing.

This is dependent on the module 'tree', which contains the classes used to
build the parse hierarchy.

@author: James
'''

from pyparsing import *
from parsetree import *

singleSlash = Literal("/")
doubleSlash = Literal("//")
stepSeparator = doubleSlash | singleSlash

reverseAxis = Combine(oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") + "::")
forwardAxis = Combine(oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") + "::")

ncName = Word(alphas + '_', alphanums + '.-')
qName = Optional(ncName + ':') + ncName

reverseStep = (reverseAxis + nodeTest) | Literal('..')
forwardStep = (forwardAxis + nodeTest) | (Optional('@') + nodeTest)

step = forwardStep | reverseStep
relativePathExpr = step + ZeroOrMore((Literal("//") | Literal("/")) + step)

#pathExpr = (Literal("//") + relativePathExpr) | (Literal("/") + Optional(relativePathExpr)) | relativePathExpr
pathExpr = (Optional(stepSeparator) + relativePathExpr) | Literal("/") 

def handleQName(s, loc, tokens):
    if len(tokens) is 3:
        return QName(tokens[0], tokens[2])
    else:
        return QName(None, tokens[0])

qName.setParseAction(handleQName)

def test(string, parser=qName):
    try:
        print (string)
        print (parser.parseString(string))
    except ParseException as err:
        print (err)
        
if __name__ == '__main__':
    test('nodeA')
    #test('1node')
    #test('')
    test('a:node')
    #test(':node')
    test('an:node')

