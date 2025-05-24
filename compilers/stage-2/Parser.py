from Lexer import *
from Translator import *
from Type import *


class Parser:
    lexer = None
    token = None

    def __init__(self, filepath):
        self.lexer = Lexer(filepath)
        self.token = None

        self.firstPrimaryExpression = set(
            (Tag.ID, Tag.NUMBER, Tag.TRUE, Tag.FALSE, ord("("))
        )

        self.firstUnaryExpression = self.firstPrimaryExpression.union(
            set((ord("-"), ord("!")))
        )

        self.firstExtendedMultiplicativeExpression = set((ord("*"), ord("/"), Tag.MOD))

        self.firstMultiplicativeExpression = self.firstUnaryExpression

        self.firstExtendedAdditiveExpression = set((ord("+"), ord("-")))

        self.firstAdditiveExpression = self.firstMultiplicativeExpression

        self.firstExtendedRelationalExpression = set(
            (ord("<"), ord(">"), Tag.GEQ, Tag.LEQ)
        )

        self.firstRelationalExpression = self.firstAdditiveExpression

        self.firstExtendedEqualityExpression = set((ord("="), Tag.NEQ))

        self.firstEqualityExpression = self.firstRelationalExpression

        self.firstExtendedConditionalTerm = set([Tag.AND])

        self.firstConditionalTerm = self.firstEqualityExpression

        self.firstExtendedConditionalExpression = set([Tag.OR])

        self.firstConditionalExpression = self.firstConditionalTerm

        self.firstExpression = self.firstConditionalExpression

        self.firstSetXYStatement = set([Tag.SETXY])

        self.firstSetXStatement = set([Tag.SETX])

        self.firstSetYStatement = set([Tag.SETY])

        self.firstLeftStatement = set([Tag.LEFT])

        self.firstRightStatement = set([Tag.RIGHT])

        self.firstBackwardStatement = set([Tag.BACKWARD])

        self.firstForwardStatement = set([Tag.FORWARD])

        self.firstMovementStatement = self.firstForwardStatement.union(
            self.firstBackwardStatement,
            self.firstRightStatement,
            self.firstLeftStatement,
            self.firstSetXStatement,
            self.firstSetYStatement,
            self.firstSetXYStatement,
            [Tag.HOME],
        )

        self.firstDrawingStatement = set(
            (
                Tag.CLEAR,
                Tag.CIRCLE,
                Tag.ARC,
                Tag.PENUP,
                Tag.PENDOWN,
                Tag.COLOR,
                Tag.PENWIDTH,
            )
        )

        self.firstSimpleStatement = set([Tag.VAR, Tag.ID, Tag.PRINT]).union(
            self.firstMovementStatement, self.firstDrawingStatement
        )

        self.firstConditionalStatement = set((Tag.IF, Tag.IFELSE))

        self.firstStructuredStatement = set([Tag.WHILE]).union(
            self.firstConditionalStatement
        )

        self.firstProgram = set([Tag.VAR])

        self.firstStatement = self.firstSimpleStatement.union(
            self.firstStructuredStatement
        )

        self.firstStatementSequence = self.firstStatement

        self.firstElement = set([Tag.STRING]).union(self.firstExpression)

    def error(self, extra=None):
        text = "Line " + str(self.lexer.line) + " - "
        if extra == None:
            text = text + "."
        else:
            text = text + extra
        raise Exception(text)

    def check(self, tag):
        if self.token.tag == tag:
            self.token = self.lexer.scan()
        else:
            text = "Line " + str(self.lexer.line) + " - expected "
            if tag != Tag.ID:
                text = text + str(Token(tag)) + " before " + str(self.token)
            else:
                text = text + "an identifier before " + str(self.token)
            self.error(text)

    def analize(self):
        self.token = self.lexer.scan()
        return self.program()

    def primaryExpression(self):
        if self.token.tag in self.firstPrimaryExpression:
            if self.token.tag == Tag.ID:
                # semantic action #
                current = self.token
                # semantic action #

                self.check(Tag.ID)

                # semantic action #
                return Identifier(current.value, self.lexer.line)
                # semantic action #
            elif self.token.tag == Tag.NUMBER:
                # semantic action #
                current = self.token
                # semantic action #

                self.check(Tag.NUMBER)

                # semantic action #
                return Number(current.value)
                # semantic action #
            elif self.token.tag == Tag.TRUE:
                self.check(Tag.TRUE)

                # semantic action #
                return Boolean(True)
                # semantic action #
            elif self.token.tag == Tag.FALSE:
                self.check(Tag.FALSE)

                # semantic action #
                return Boolean(False)
                # semantic action #
            elif self.token.tag == ord("("):
                self.check(ord("("))

                # semantic action #
                node = self.expression()
                # semantic action #

                self.check(ord(")"))

                # semantic action #
                return node
                # semantic action #
        else:
            self.error("expected a primary expression before " + str(self.token))

    def unaryExpression(self):
        if self.token.tag in self.firstUnaryExpression:
            if self.token.tag == ord("-"):
                self.check(ord("-"))

                # semantic action #
                right = self.unaryExpression()
                return Minus(right)
                # semantic action #
            elif self.token.tag == ord("!"):
                self.check(ord("!"))

                # semantic action #
                right = self.unaryExpression()
                return Not(right)
                # semantic action #
            else:
                # semantic action #
                return self.primaryExpression()
                # semantic action #
        else:
            self.error("expected an unary expression before " + str(self.token))

    def extendedMultiplicativeExpression(self, left):
        if self.token.tag in self.firstExtendedMultiplicativeExpression:
            if self.token.tag == ord("*"):
                self.check(ord("*"))

                # semantic action #
                right = self.unaryExpression()
                node = Multiply(left, right)
                return self.extendedMultiplicativeExpression(node)
                # semantic action #
            elif self.token.tag == ord("/"):
                self.check(ord("/"))

                # semantic action #
                right = self.unaryExpression()
                node = Divide(left, right, self.lexer.line)
                return self.extendedMultiplicativeExpression(node)
                # semantic action #
            elif self.token.tag == Tag.MOD:
                self.check(Tag.MOD)

                # semantic action #
                right = self.unaryExpression()
                node = Module(left, right, self.lexer.line)
                return self.extendedMultiplicativeExpression(node)
                # semantic action #
        else:
            return left

    def multiplicativeExpression(self):
        if self.token.tag in self.firstMultiplicativeExpression:
            # semantic action #
            left = self.unaryExpression()
            return self.extendedMultiplicativeExpression(left)
            # semantic action #
        else:
            self.error(
                "expected an multiplicative expression before " + str(self.token)
            )

    def extendedAdditiveExpression(self, left):
        if self.token.tag in self.firstExtendedAdditiveExpression:
            if self.token.tag == ord("+"):
                self.check(ord("+"))

                # semantic action #
                right = self.multiplicativeExpression()
                node = Add(left, right)
                return self.extendedAdditiveExpression(node)
                # semantic action #
            elif self.token.tag == ord("-"):
                self.check(ord("-"))

                # semantic action #
                right = self.multiplicativeExpression()
                node = Substract(left, right)
                return self.extendedAdditiveExpression(node)
                # semantic action #
        else:
            return left

    def additiveExpression(self):
        if self.token.tag in self.firstAdditiveExpression:
            # semantic action #
            left = self.multiplicativeExpression()
            return self.extendedAdditiveExpression(left)
            # semantic action #
        else:
            self.error("expected an additive expression before " + str(self.token))

    def extendedRelationalExpression(self, left):
        if self.token.tag in self.firstExtendedRelationalExpression:
            if self.token.tag == ord("<"):
                self.check(ord("<"))

                # semantic action #
                right = self.additiveExpression()
                node = Lesser(left, right)
                return self.extendedRelationalExpression(node)
                # semantic action #
            elif self.token.tag == Tag.LEQ:
                self.check(Tag.LEQ)

                # semantic action #
                right = self.additiveExpression()
                node = LesserOrEqual(left, right)
                return self.extendedRelationalExpression(node)
                # semantic action #
            elif self.token.tag == ord(">"):
                self.check(ord(">"))

                # semantic action #
                right = self.additiveExpression()
                node = Greater(left, right)
                return self.extendedRelationalExpression(node)
                # semantic action #
            elif self.token.tag == Tag.GEQ:
                self.check(Tag.GEQ)

                # semantic action #
                right = self.additiveExpression()
                node = GreaterOrEqual(left, right)
                return self.extendedRelationalExpression(node)
                # semantic action #
        else:
            return left

    def relationalExpression(self):
        if self.token.tag in self.firstRelationalExpression:
            # semantic action #
            left = self.additiveExpression()
            return self.extendedRelationalExpression(left)
            # semantic action #
        else:
            self.error("expected an relational expression before " + str(self.token))

    def extendedEqualityExpression(self, left):
        if self.token.tag in self.firstExtendedEqualityExpression:
            if self.token.tag == ord("="):
                self.check(ord("="))
                right = self.relationalExpression()
                node = Equal(left, right)
                return self.extendedEqualityExpression(node)
            elif self.token.tag == Tag.NEQ:
                self.check(Tag.NEQ)
                right = self.relationalExpression()
                node = Different(left, right)
                return self.extendedEqualityExpression(node)
        else:
            return left

    def equalityExpression(self):
        if self.token.tag in self.firstEqualityExpression:
            left = self.relationalExpression()
            return self.extendedEqualityExpression(left)
        else:
            self.error("expected equality expression before" + str(self.token))

    def extendedConditionalTerm(self, left):
        if self.token.tag in self.firstExtendedConditionalTerm:
            self.check(Tag.AND)
            right = self.equalityExpression()
            node = And(left, right)
            return self.extendedConditionalTerm(node)
        else:
            return left

    def conditionalTerm(self):
        if self.token.tag in self.firstConditionalTerm:
            left = self.equalityExpression()
            return self.extendedConditionalTerm(left)
        else:
            self.error("expected conditional term before" + str(self.token))

    def extendedConditionalExpression(self, left):
        if self.token.tag in self.firstExtendedConditionalExpression:
            self.check(Tag.OR)
            right = self.conditionalTerm()
            node = Or(left, right)
            return self.extendedConditionalExpression(node)
        else:
            return left

    def conditionalExpression(self):
        if self.token.tag in self.firstConditionalExpression:
            left = self.conditionalTerm()
            return self.extendedConditionalExpression(left)
        else:
            self.error("expected conditional expression before" + str(self.token))

    def expression(self):
        if self.token.tag in self.firstExpression:
            return self.conditionalExpression()
        else:
            self.error("expected expression before" + str(self.token))

    def ifElseStatement(self):
        if self.token.tag == Tag.IFELSE:
            self.check(Tag.IFELSE)
            self.check(ord("("))
            condition = self.expression()
            self.check(ord(")"))
            self.check(ord("["))
            ifSequence = self.statementSequence()
            self.check(ord("]"))
            self.check(ord("["))
            elseSequence = self.statementSequence()
            self.check(ord("]"))
            return IfElse(condition, ifSequence, elseSequence)
        else:
            self.error("expected an IFELSE expression before " + str(self.token))

    def ifStatement(self):
        if self.token.tag == Tag.IF:
            self.check(Tag.IF)
            self.check(ord("("))
            condition = self.expression()
            self.check(ord(")"))
            self.check(ord("["))
            sequence = self.statementSequence()
            self.check(ord("]"))
            return If(condition, sequence)
        else:
            self.error("expected an IF expression before " + str(self.token))

    def conditionalStatement(self):
        if self.token.tag in self.firstConditionalStatement:
            if self.token.tag == Tag.IF:
                return self.ifStatement()
            elif self.token.tag == Tag.IFELSE:
                return self.ifElseStatement()
        else:
            self.error("expected an conditional expression before " + str(self.token))

    def repetitiveStatement(self):
        if self.token.tag == Tag.WHILE:
            self.check(Tag.WHILE)
            self.check(ord("("))
            condition = self.expression()
            self.check(ord(")"))
            self.check(ord("["))
            sequence = self.statementSequence()
            self.check(ord("]"))
            return While(condition, sequence)
        else:
            self.error("expected an repetitive expression before " + str(self.token))

    def structuredStatement(self):
        if self.token.tag in self.firstStructuredStatement:
            if self.token.tag in self.firstConditionalStatement:
                return self.conditionalStatement()
            elif self.token.tag == Tag.WHILE:
                return self.repetitiveStatement()
        else:
            self.error("expected an structured expression before " + str(self.token))

    def element(self):
        if self.token.tag in self.firstElement:
            if self.token.tag == Tag.STRING:
                node = String(self.token.value)
                self.check(Tag.STRING)
                return node
            elif self.token.tag in self.firstExpression:
                return self.expression()
        else:
            self.error("expected an element expression before " + str(self.token))

    def elementList(self, elementList=None):
        if self.token.tag == ord(","):
            self.check(ord(","))
            element = self.element()
            node = ElementList(element, elementList)
            return self.elementList(node)
        else:
            return elementList

    def textStatement(self):
        if self.token.tag == Tag.PRINT:
            self.check(Tag.PRINT)
            self.check(ord("("))
            element = self.element()
            elementList = self.elementList()
            self.check(ord(")"))
            return Print(element, elementList)
        else:
            self.error("expected a PRINT statement before " + str(self.token))

    def penWidthStatement(self):
        if self.token.tag == Tag.PENWIDTH:
            self.check(Tag.PENWIDTH)
            self.check(ord("("))
            expression = self.expression()
            self.check(ord(")"))
            return PenWidth(expression)
        else:
            self.error("expected a PENWIDTH statement before " + str(self.token))

    def colorStatement(self):
        if self.token.tag == Tag.COLOR:
            self.check(Tag.COLOR)
            self.check(ord("("))
            r = self.expression()
            self.check(ord(","))
            g = self.expression()
            self.check(ord(","))
            b = self.expression()
            self.check(ord(")"))
            return Color(r, g, b, self.lexer.line)
        else:
            self.error("expected a COLOR statement before " + str(self.token))

    def penDownStatement(self):
        if self.token.tag == Tag.PENDOWN:
            self.check(Tag.PENDOWN)
            self.check(ord("("))
            self.check(ord(")"))
            return PenDown()
        else:
            self.error("expected a PENDOWN statement before " + str(self.token))

    def penUpStatement(self):
        if self.token.tag == Tag.PENUP:
            self.check(Tag.PENUP)
            self.check(ord("("))
            self.check(ord(")"))
            return PenUp()
        else:
            self.error("expected a PENUP statement before " + str(self.token))

    def arcStatement(self):
        if self.token.tag == Tag.ARC:
            self.check(Tag.ARC)
            self.check(ord("("))
            radius = self.expression()
            self.check(ord(","))
            degrees = self.expression()
            self.check(ord(")"))
            return Arc(radius, degrees)
        else:
            self.error("expected a ARC statement before " + str(self.token))

    def circleStatement(self):
        if self.token.tag == Tag.CIRCLE:
            self.check(Tag.CIRCLE)
            self.check(ord("("))
            radius = self.expression()
            self.check(ord(")"))
            return Circle(radius)
        else:
            self.error("expected a CIRCLE statement before " + str(self.token))

    def clearStatement(self):
        if self.token.tag == Tag.CLEAR:
            self.check(Tag.CLEAR)
            self.check(ord("("))
            self.check(ord(")"))
            return Clear()
        else:
            self.error("expected a CLEAR statement before " + str(self.token))

    def drawingStatement(self):
        if self.token.tag in self.firstDrawingStatement:
            if self.token.tag == Tag.CLEAR:
                return self.clearStatement()
            elif self.token.tag == Tag.CIRCLE:
                return self.circleStatement()
            elif self.token.tag == Tag.ARC:
                return self.arcStatement()
            elif self.token.tag == Tag.PENUP:
                return self.penUpStatement()
            elif self.token.tag == Tag.PENDOWN:
                return self.penDownStatement()
            elif self.token.tag == Tag.COLOR:
                return self.colorStatement()
            elif self.token.tag == Tag.PENWIDTH:
                return self.penWidthStatement()
        else:
            self.error("expected a drawing statement before " + str(self.token))

    def setXYStatement(self):
        if self.token.tag in self.firstSetXYStatement:
            self.check(Tag.SETXY)
            self.check(ord("("))
            x = self.expression()
            self.check(ord(","))
            y = self.expression()
            self.check(ord(")"))
            return SetXY(x, y)
        else:
            self.error("expected a setXY statement before " + str(self.token))

    def setXStatement(self):
        if self.token.tag in self.firstSetXStatement:
            self.check(Tag.SETX)
            self.check(ord("("))
            x = self.expression()
            self.check(ord(")"))
            return SetX(x)
        else:
            self.error("expected a setX statement before " + str(self.token))

    def setYStatement(self):
        if self.token.tag in self.firstSetYStatement:
            self.check(Tag.SETY)
            self.check(ord("("))
            y = self.expression()
            self.check(ord(")"))
            return SetY(y)
        else:
            self.error("expected a setY statement before " + str(self.token))

    def leftStatement(self):
        if self.token.tag in self.firstLeftStatement:
            self.check(Tag.LEFT)
            self.check(ord("("))
            angle = self.expression()
            self.check(ord(")"))
            return Left(angle)
        else:
            self.error("expected a left statement before " + str(self.token))

    def rightStatement(self):
        if self.token.tag in self.firstRightStatement:
            self.check(Tag.RIGHT)
            self.check(ord("("))
            angle = self.expression()
            self.check(ord(")"))
            return Right(angle)
        else:
            self.error("expected a right statement before " + str(self.token))

    def backwardStatement(self):
        if self.token.tag in self.firstBackwardStatement:
            self.check(Tag.BACKWARD)
            self.check(ord("("))
            distance = self.expression()
            self.check(ord(")"))
            return Backward(distance)
        else:
            self.error("expected a backward statement before " + str(self.token))

    def forwardStatement(self):
        if self.token.tag in self.firstForwardStatement:
            self.check(Tag.FORWARD)
            self.check(ord("("))
            distance = self.expression()
            self.check(ord(")"))
            return Forward(distance)
        else:
            self.error("expected a forward statement before " + str(self.token))

    def movementStatement(self):
        if self.token.tag in self.firstMovementStatement:
            if self.token.tag == Tag.FORWARD:
                return self.forwardStatement()
            elif self.token.tag == Tag.BACKWARD:
                return self.backwardStatement()
            elif self.token.tag == Tag.RIGHT:
                return self.rightStatement()
            elif self.token.tag == Tag.LEFT:
                return self.leftStatement()
            elif self.token.tag == Tag.SETX:
                return self.setXStatement()
            elif self.token.tag == Tag.SETY:
                return self.setYStatement()
            elif self.token.tag == Tag.SETXY:
                return self.setXYStatement()
            else:
                self.check(Tag.HOME)
                self.check(ord("("))
                self.check(ord(")"))
                return Home()
        else:
            self.error("expected a movement statement before " + str(self.token))

    def assignmentStatement(self):
        if self.token.tag == Tag.ID:
            id = self.token.value
            line = self.lexer.line
            self.check(Tag.ID)
            self.check(Tag.ASSIGN)
            exp = self.expression()
            return Assignment(id, exp, line)
        else:
            self.error("expected an ASSIGNMENT statement before " + str(self.token))

    def identifierList(self, idList):
        if self.token.tag == ord(","):
            self.check(ord(","))
            id = IdDeclaration(self.token.value, self.lexer.line)
            self.check(Tag.ID)
            node = idDeclarationList(id, idList)
            return self.identifierList(node)
        else:
            return idList

    def declarationStatement(self):
        if self.token.tag == Tag.VAR:
            self.check(Tag.VAR)
            node = IdDeclaration(self.token.value, self.lexer.line)
            self.check(Tag.ID)
            nodeList = self.identifierList(None)
            return Declaration(node, nodeList)
        else:
            self.error("expected a DECLARATION statement before " + str(self.token))

    def simpleStatement(self):
        if self.token.tag in self.firstSimpleStatement:
            if self.token.tag == Tag.VAR:
                return self.declarationStatement()
            elif self.token.tag == Tag.ID:
                return self.assignmentStatement()
            elif self.token.tag in self.firstMovementStatement:
                return self.movementStatement()
            elif self.token.tag in self.firstDrawingStatement:
                return self.drawingStatement()
            elif self.token.tag == Tag.PRINT:
                return self.textStatement()
        else:
            self.error(
                "expected a simple statement statement before " + str(self.token)
            )

    def statement(self):
        if self.token.tag in self.firstStatement:
            if self.token.tag in self.firstSimpleStatement:
                return self.simpleStatement()
            elif self.token.tag in self.firstStructuredStatement:
                return self.structuredStatement()
        else:
            self.error("expected a statement before " + str(self.token))

    def statementSequence(self):
        if self.token.tag in self.firstStatementSequence:
            statement = self.statement()
            sequence = self.statementSequence()
            return StatementSequence(statement, sequence)
        else:
            return None

    def program(self):
        statements = self.statementSequence()
        if self.token.tag == Tag.EOF:
            return Program(statements)
        else:
            print(str(self.token))
            self.error("ilegal start of a statement")
