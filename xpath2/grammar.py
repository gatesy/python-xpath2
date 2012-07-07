'''
Created on 6 Jul 2012

A full XPath2 grammar parser using the pyparsing module.
This is based on the EBNF grammar specification for XPath2 given here: http://www.w3.org/TR/xpath20/#nt-bnf 

@author: James
'''

from pyparsing import *

# Start by doing grammar for path expressions:

# First get the terminal names: QName and NCName
ncName = Word(alphas+"_", alphanums+"-.")
unprefixedName = ncName
prefixedName = ncName + ":" + ncName
qName = prefixedName | unprefixedName
wildcard = Literal("*") | (ncName + Literal(":*")) | (Literal("*:") + ncName)

# Variable names are simply QNames
varName = qName


# Expr is any expression
expr = Forward()
exprSingle = Forward()

# PathExpr

# Terminals: /, // and axis
reverseAxis = oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") + "::"
forwardAxis = oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") + "::"
generalComp = oneOf("= != <= < >= >")
valueComp = Keyword("eq") | Keyword("ne") | Keyword("lt") | Keyword("le") | Keyword("gt") | Keyword("ge")
nodeComp = oneOf("<< >>") | Keyword("is")

primaryExpr = literal | varRef | parenthesizedExpr | contextItemExpr | functionCall

predicate = Literal("[") + expr + Literal("]")
predicateList = ZeroOrMore(predicate)
filterExpr = primaryExpr | predicateList

nameTest = qName | wildcard
nodeTest = kindTest | nameTest

abbrevReverseStep = Literal("..")
reverseStep = (reverseAxis + nodeTest) | abbrevReverseStep

abbrevForwardStep = Optional("@") + nodeTest
forwardStep = (forwardAxis + nodeTest) | abbrevForwardStep

axisStep = (reverseStep | forwardStep) + predicateList
stepExpr = filterExpr | axisStep
relativePathExpr = stepExpr + ZeroOrMore((Literal("//") | Literal("/")) + stepExpr)
pathExpr = (Literal("//") + relativePathExpr) | (Literal("/") + Optional(relativePathExpr)) | relativePathExpr

valueExpr = pathExpr
unaryExpr = ZeroOrMore(Literal("-") | Literal("+")) + valueExpr
castExpr = unaryExpr + Optional(Keyword("cast") + Keyword("as") + singleType)
castableExpr = castExpr + Optional(Keyword("castable") + Keyword("as") + singleType)
treatExpr = castableExpr + Optional(Keyword("treat") + Keyword("as") + sequenceType)
instnaceofExpr = treatExpr + Optional(Keyword("instance") + Keyword("of") + sequenceType)
intersectExceptExpr = instanceofExpr + ZeroOrMore((Keyword("intersect") | Keyword("except")) + instanceofExpr)
unionExpr = intersectExceptExpr + ZeroOrMore((Keyword("union") | Literal("|")) + intersectExceptExpr)
multiplicativeExpr = (unionExpr + ZeroOrMore((Literal("*") | Keyword("div") | Keyword("idiv") | 
                                              Keyword("mod")) + unionExpr))
additiveExpr = multiplicativeExpr + ZeroOrMore((Literal("+") | Literal("-")) + multiplicativeExpr)
rangeExpr = additiveExpr + Optional(Keyword("to") + additiveExpr)
comparisonExpr = rangeExpr + Optional((valueComp | generalComp | nodeComp) + rangeExpr)

andExpr = comparisonExpr + ZeroOrMore(Keyword("and") + comparisonExpr)
orExpr = andExpr + ZeroOrMore(Keyword("or") + andExpr)

ifExpr = (Keyword("if") + Literal("(") + expr + Literal(")") + Keyword("then") + exprSingle + 
    Keyword("else") + exprSingle)

quantifiedExpr = ((Keyword("some") | Keyword("every")) + Literal("$") + varName + Keyword("in") + 
    exprSingle + ZeroOrMore(Literal(",") + Literal("$") + varName + Keyword("in") + exprSingle) + 
    Keyword("satisfies") + exprSingle)

simpleForClause = (Keyword("for") + Literal("$") + varName + Keyword("in") + exprSingle 
    + ZeroOrMore(Literal(",") + Literal("$") + varName + Keyword("in") + exprSingle))
forExpr = simpleForClause + Keyword("return") + exprSingle

exprSingle << (forExpr | quantifiedExpr | ifExpr | orExpr) 
expr << (exprSingle + ZeroOrMore(Literal(",") + exprSingle))

xpath = expr

def test(strParam):
    try:
        print (strParam)
        print (xpath.parseString(strParam))
    except ParseException as err:
        print (err)
        
test("node")
test("parent::node")
test("node1/node2")
test("/node")
test("@attribute")
test("//a/b/c")
test("//node1/b/*//fg/@test")    
