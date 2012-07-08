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

digits = Word(nums)
integerLiteral = digits
decimalLiteral = (Literal(".") + digits) | (digits + Literal(".") + ZeroOrMore(nums))
doubleLiteral = (((Literal(".") + digits) | (digits + Optional(Literal(".") + ZeroOrMore(nums)))) + 
                 oneOf("e E") + Optional(oneOf("- +")) + digits)

escapeQuot = Literal('""')
escapeApos = Literal("''")
stringLiteral = ((Literal('"') + ZeroOrMore(escapeQuot | CharsNotIn('"')) + Literal('"')) | 
                  (Literal("'") + ZeroOrMore(escapeApos | CharsNotIn("'") + Literal("'")))) 

commentContents = (Word(printables) - (ZeroOrMore(printables) +  
                                       (Literal("(:") | Literal(":)")) + ZeroOrMore(printables)))
comment = Forward()
comment << Literal("(:") + ZeroOrMore(commentContents | comment) + Literal(":)")

# Variable names are simply QNames
varName = qName


# Expr is any expression
expr = Forward()
exprSingle = Forward()

# PathExpr

# Terminals: /, // and axis
reverseAxis = Combine(oneOf("parent ancestor preceding-sibling preceding ancestor-or-self") + "::")
forwardAxis = Combine(oneOf("child descendant attribute self descendant-or-self following-sibling following namespace") + "::")
generalComp = oneOf("= != <= < >= >")
valueComp = Keyword("eq") | Keyword("ne") | Keyword("lt") | Keyword("le") | Keyword("gt") | Keyword("ge")
nodeComp = oneOf("<< >>") | Keyword("is")
contextItemExpr = Literal(".")
occuranceIndicator = oneOf("? * +")

typeName = qName
elementName = qName
attributeName = qName

elementDeclaration = elementName
schemaElementTest = Literal("schema-element") + Literal("(") + elementDeclaration + Literal(")")
elementNameOrWildcard = elementName | Literal("*")
elementTest = (Literal("element") + Literal("(") + 
               Optional(elementNameOrWildcard + Optional(Literal(",") + typeName + Optional("?"))) + Literal(")"))

attributeDeclaration = attributeName
schemaAttributeTest = Literal("schema-attribute") + Literal("(") + attributeDeclaration + Literal(")")
attribNameOrWildcard = attributeName | Literal("*")
attributeTest = (Literal("attribute") + Literal("(") + attribNameOrWildcard + 
                 Optional(Literal(",") + typeName) + Literal(")"))

piTest = Literal("processing-instruction") + Literal("(") + Optional(ncName | stringLiteral) + Literal(")")
commentTest = Literal("comment") + Literal("(") + Literal(")")
textTest = Literal("text") + Literal("(") + Literal(")")
documentTest = Literal("document-node") + Literal("(") + Optional(elementTest | schemaElementTest) + Literal(")")
anyKindTest = Literal("node") + Literal("(") + Literal(")")
kindTest = (documentTest | elementTest | attributeTest | schemaElementTest | schemaAttributeTest | piTest |
            commentTest | textTest | anyKindTest)

atomicType = qName
itemType = kindTest | (Literal("item") + Literal("(") + Literal(")")) | atomicType
sequenceType = (Literal("empty-sequence") + Literal("(") + Literal(")")) | (itemType + Optional(occuranceIndicator))
singleType = atomicType + Optional(Literal("?"))

functionCall = qName + Literal("(") + Optional(exprSingle + ZeroOrMore(Literal(",") + exprSingle)) + Literal(")")
parenthesizedExpr = Literal("(") + Optional(expr) + Literal(")")
varRef = Literal("$") + varName

numericLiteral = integerLiteral | decimalLiteral | doubleLiteral
literal = numericLiteral | stringLiteral
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
stepExpr = filterExpr ^ axisStep
relativePathExpr = stepExpr + ZeroOrMore((Literal("//") ^ Literal("/")) + stepExpr)
pathExpr = (Literal("//") + relativePathExpr) | (Literal("/") + Optional(relativePathExpr)) | relativePathExpr

valueExpr = pathExpr
unaryExpr = ZeroOrMore(Literal("-") | Literal("+")) + valueExpr
castExpr = unaryExpr + Optional(Keyword("cast") + Keyword("as") + singleType)
castableExpr = castExpr + Optional(Keyword("castable") + Keyword("as") + singleType)
treatExpr = castableExpr + Optional(Keyword("treat") + Keyword("as") + sequenceType)
instanceofExpr = treatExpr + Optional(Keyword("instance") + Keyword("of") + sequenceType)
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
