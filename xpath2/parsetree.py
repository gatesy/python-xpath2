'''
Created on 8 Jul 2012

Classes for representing nodes in the parse tree of an XPath2 expression

@author: James
'''

from decimal import Decimal

class Expr(object):
    def __init__(self, tokens):
        print(str(tokens))
        
    def __repr__(self):
        return 'Expr'

class QName(object):
    def __init__(self, tokens):
        if len(tokens) is 3:
            self.ns = tokens[0]
            self.name= tokens[2]
        else:
            self.ns = None
            self.name = tokens[0]
        
    def __repr__(self):
        s = 'QName('
        if not(self.ns is None):
            s += self.ns + ':'
        s += self.name + ')'
        return s

    def match(self, element):
        if self.name == element.tag:
            return element
        else:
            return None
    
class Wildcard(object):
    def __init__(self, tokens):
        self.tokens = tokens
        
    def __repr__(self):
        return 'Wildcard(' + str(self.tokens) + ')'

#
# Literals
#
class IntegerLiteral(object):
    value = None
    
    def __init__(self, tokens):
        self.number = tokens[0]
        
    def __repr__(self):
        return 'IntegerLiteral(' + str(self.number) + ')'

    def getValue(self):
        if self.value is None:
            self.value = int(self.number)
        return self.value

class DecimalLiteral(object):
    leftNumber = '0'
    rightNumber = '0'
    value = None
    
    def __init__(self, tokens):
        if len(tokens) == 3:
            self.leftNumber = tokens[0]
            self.rightNumber = tokens[2]
        elif tokens[0] == '.':
            self.rightNumber = tokens[1]
        else: 
            self.leftNumber = tokens[0]
        
    def getValue(self):
        if self.value is None:
            self.value = Decimal(self.leftNumber + '.' + self.rightNumber)
        return self.value
        
    def __repr__(self):
        return 'DecimalLiteral(' + str(self.leftNumber) + '.' + str(self.rightNumber) + ')'

class DoubleLiteral(object):
    value = None
    
    def __init__(self, tokens):
        self.base = tokens[0]
        self.exponent = tokens[2:]
        
    def __repr__(self):
        return 'DoubleLiteral(' + str(self.base) + 'e' + str(self.exponent) + ')'

    def getValue(self):
        if self.value is None:
            self.value = float(str(self.base.getValue()) + 'e' + ''.join(self.exponent))
        return self.value
        
class EscapedDblQuote(object):
    value = '"'
    
    def __init__(self, tokens):
        pass
        
    def __repr__(self):
        return self.value
    
class EscapedSglQuote(object):
    value = "'"
    
    def __init__(self, tokens):
        pass

    def __repr__(self):
        return self.value
        
    def __str__(self):
        return self.value

class StringLiteral(object):
    value = None
    
    def __init__(self, tokens):
        self.parts = tokens[1:len(tokens)-1]
        
    def getValue(self):
        if self.value is None:
            self.value = ''.join(map(str, self.parts))
        return self.value
        
    def __repr__(self):
        return 'StringLiteral(' + str(self.parts) + ')'

class VariableRef(object):
    
    def __init__(self, tokens):
        self.name = tokens[1]
        
    def __repr__(self):
        return 'VariableRef(' + str(self.name) + ')'

class UnaryOp(object):
    expr = None
    op = None
    
    def __init__(self, tokens):
        self.op = tokens[0]
        self.expr = tokens[1]
        
    def __repr__(self):
        return str(self.op) + '(' + str(self.expr) + ')'

class UnaryOpRightAssoc(UnaryOp):
    def __init__(self, tokens):
        self.op = tokens[0]
        if len(tokens) == 2:
            self.expr = tokens[1]
        elif len(tokens) > 2:
            self.expr = UnaryOpRightAssoc(tokens[1:])
        else:
            raise ValueError('Expected at least 2 tokens')

def unaryOpRightAssocHelper(tokens):
    if len(tokens) > 1:
        return UnaryOpRightAssoc(tokens)
    else:
        return tokens

class BinaryOp(object):
    left = None
    op = None
    right = None
    
    def __init__(self, tokens):
        self.left = tokens[0]
        if len(tokens) > 1:
            self.op = tokens[1]
        if len(tokens) == 3:
            self.right = tokens[2]
        else:
            self.right = BinaryOp(tokens[2:])
        
    def __repr__(self):
        return str(self.op) + '(' + str(self.left) + ',' + str(self.right) + ')'

class BinaryOpLeftAssoc(BinaryOp):
    def __init__(self, tokens, opTokens=1):
        if len(tokens) > (2 + opTokens):
            self.right = tokens[-1]
            self.op = '-'.join(tokens[-(1+opTokens):-1])
            self.left = BinaryOpLeftAssoc(tokens[:-1-opTokens])
        else:
            self.left = tokens[0]
            self.op = '-'.join(tokens[1:1+opTokens])
            self.right = tokens[1 + opTokens]

def binaryOpHelper(tokens):
    if len(tokens) > 1:
        return BinaryOp(tokens)
    else:
        return tokens

def binaryOpLeftAssocHelper(tokens):
    if len(tokens) > 1:
        return BinaryOpLeftAssoc(tokens)
    else:
        return tokens  
        
def binaryOpLeftAssocHelper2(tokens):
    if len(tokens) > 1:
        return BinaryOpLeftAssoc(tokens, 2)
    else:
        return tokens

class KindTest(object):
    pass

class AnyKindTest(KindTest):
    pass

class TextTest(KindTest):
    pass

class CommentTest(KindTest):
    pass

class Step(object):
    def __init__(self, tokens):
        self.axis = tokens[0]
        self.nodeTest = tokens[2]
        self.predicates = tokens[3:]
        
    def match(self, element):
        if self.axis == 'child':
            return self.nodeTest.match(element)
        
    def __repr__(self):
        return 'Step(axis=' + repr(self.axis) + '; nodeTest=' + repr(self.nodeTest) + '; predicates=' \
            + repr(self.predicates) + ')'

class Predicate(object):
    def __init__(self, tokens):
        self.expr = tokens[1]
        
    def __repr__(self):
        return 'Predicate(expr=' + repr(self.expr) + ')'
        
class ContextItem(object):
    def __init__(self,tokens):
        pass
        
    def __repr__(self):
        return 'ContextItem'
        
class FunctionCall(object):
    def __init__(self, tokens):
        pass
        
    def __repr(self):
        return 'FunctionCall'
