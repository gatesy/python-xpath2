'''
Created on 8 Jul 2012

The evaluation context for an XPath2 expression.

@author: James
'''

class Context(object):
    def __init__(self, expr, node):
        self.node = node
        self.expr = expr
    
    def __repr__(self):
        return 'node=' + str(self.node) + '; expr=' + str(self.expr)  
        
    def process(self):
        if not self.node is None and len(self.expr) > 0:
            parseNode = self.expr[0]
            matchedElements = parseNode.match(self.node)
            return matchedElements