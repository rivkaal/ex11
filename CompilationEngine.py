"""
This module effects the actual compilation into XML form. It gets its input from a JackTokenizer and
writes its parsed XML structure into an output file/stream. This is done by a series of compilexxx()
methods, where xxx is a corresponding syntactic element of the Jack grammar. The contract between these
methods is that each compilexxx() method should read the syntactic construct xxx from the input,
advance() the tokenizer exactly beyond xxx, and output the XML parsing of xxx. Thus,
compilexxx()may only be called if indeed xxx is the next syntactic element of the input.
"""

import SymbolTable as ST
import VMWriter as VM

LABELS_IN_IF_IMPLEMENTATION = 2

#hey!!!
class Parsing:

    subDecList = {'constructor', 'function', 'method'}
    classVarTypes = {'int', 'char', 'boolean'}
    operations = {'+','-','=','*','/','|','&','<','>'}
    opDic = {'+':'add','-':'sub','&':'and','|':'or','<':'lt','>':'gt','=':'eq'}
    keywordConst = {'true', 'false', 'null', 'this'}
    label_count = 0

    def __init__(self, token, path):
        """
        creates a new compilation engine with the given input and output.
        The next method called must be compileClass().
        :param input:stream/file
        """
        self.outFile = open(path, 'w')
        self.VM = VM.VMWriter(path)
        self.myToken = token
        self.myToken.advance()
        self.classTable = ST.SymbolTable()
        self.subTable = ST.SymbolTable()
        self.CompileClass()

        return

    def CompileClass(self):
        """
        compiles a complete class.
        :return:
        """
        self.myToken.advance()
        if self.myToken.tokenType() == 'identifier':
            className = self.myToken.identifier()
            self.eat()
        if self.myToken.tokenType() == 'symbol':
            self.eat('{')
        if self.myToken.tokenType() == 'keyword':
            if self.ifClassVarDec():
                while(self.ifClassVarDec()):
                    self.CompileClassVarDec()
            while(self.myToken.keyWord() in self.subDecList):
                if self.myToken.keyWord() == 'method':
                    self.subTable.define('this', className, 'argument')
                self.CompileSubroutine()
        self.eat('}')
        self.outFile.write('</class>\n')
        return

    def CompileClassVarDec(self):
        """
        compiles a static declaration or a field declaration.
        :return:
        """

        if self.myToken.keyWord() == 'static':
            kind = 'static'
            self.eat()
        elif self.myToken.keyWord() == 'field':
            kind = 'field'
            self.eat()
        if self.myToken.tokenType() == 'keyword':
            if self.myToken.keyWord() in self.classVarTypes :
                type = self.myToken.keyWord()
                self.eat()
        elif self.myToken.tokenType() == 'identifier':
            type = self.myToken.identifier()
            self.eat()
        else : print('expected type keyword or identifier, got '+ self.myToken.tokenType())
        if self.myToken.tokenType() == 'identifier':
            name = self.myToken.identifier()
            self.eat()
        else : print('expected identifier, got '+ self.myToken.tokenType())
        self.classTable.define(name,type, kind)
        while (self.myToken.symbol() == ','):
            self.eat(',')
            name = self.myToken.identifier()
            self.classTable.define(name,type, kind)
            self.eat()
        self.eat(';')
        return

    def CompileSubroutine(self):
        """
        compiles a complete method, function, or constructor.
        :return:
        """
        if self.myToken.tokenType() == 'keyword':
            self.eat()
        if self.myToken.tokenType() =='keyword':
            if self.myToken.keyWord() not in self.classVarTypes:
                self.eat('void') #!!!!! some void push and pomp..
            else:
                self.eat()
        elif self.myToken.tokenType() == 'identifier':
            self.eat()
        else : print('expected something else')
        if self.myToken.tokenType() == 'identifier':
            self.eat()
        else: print('expected something else')
        self.eat('(')
        self.compileParameterList()
        self.eat(')')
        self.outFile.write('<subroutineBody>\n')
        self.eat('{')
        if (self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() == 'var'):
            while (self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() == 'var'):
                self.outFile.write('<varDec>\n')
                self.compileVarDec()
                self.outFile.write('</varDec>\n')
        self.outFile.write('<statements>\n')
        self.compileStatements()
        self.outFile.write('</statements>\n')
        self.eat('}')
        self.outFile.write('</subroutineBody>\n')




        return

    def compileParameterList(self):
        """
        compiles a (possibly empty) parameter list, not including the enclosing "()".
        :return:
        """
        if self.myToken.tokenType() == 'symbol' and self.myToken.symbol() == ')':
            return

        while (self.myToken.tokenType() != 'symbol' or self.myToken.symbol() != ')'):
            if self.myToken.tokenType() == 'symbol':
                self.eat(',')
            if self.myToken.tokenType() == 'identifier':
                type = self.myToken.identifier()
                self.eat()
            elif self.myToken.tokenType() == 'keyword': #type can be keyword or identifier
                type = self.myToken.keyWord()
                self.eat()
            if self.myToken.tokenType() == 'identifier':
                name = self.myToken.identifier()
                self.subTable.define(name, type, 'argument')
                self.eat()

    def compileVarDec(self):
        """
        compiles a var declaration.
        :return:
        """
        self.eat('var')
        if self.myToken.tokenType() == 'keyword':
            if self.myToken.keyWord() in self.classVarTypes :
                type = self.myToken.keyWord()
                self.eat()
        elif self.myToken.tokenType() == 'identifier':
            type = self.myToken.identifier()
            self.eat()
        if self.myToken.tokenType() == 'identifier':
            name = self.myToken.identifier()
            self.eat()
        self.subTable.define(name, type, 'var')
        while (self.myToken.symbol() == ','):
            self.eat(',')
            name = self.myToken.identifier()
            self.eat()
            self.subTable.define(name, type, 'var')
        self.eat(';')
        return

    def compileStatements(self):
        """
        compiles a sequence os statements, not including the enclosing "{}"
        :return:
        """
        while(self.myToken.tokenType() != 'symbol' or self.myToken.symbol() != '}'):
            if self.myToken.keyWord() == 'let':
                self.outFile.write('<letStatement>\n')
                self.compileLet()
                self.outFile.write('</letStatement>\n')
            elif self.myToken.keyWord() == 'if':
                self.outFile.write('<ifStatement>\n')
                self.compileIf()
                self.outFile.write('</ifStatement>\n')
            elif self.myToken.keyWord() == 'while':
                self.outFile.write('<whileStatement>\n')
                self.compileWhile()
                self.outFile.write('</whileStatement>\n')
            elif self.myToken.keyWord() == 'do':
                self.outFile.write('<doStatement>\n')
                self.compileDo()
                self.outFile.write('</doStatement>\n')
            elif self.myToken.keyWord() == 'return':
                self.outFile.write('<returnStatement>\n')
                self.compileReturn()
                self.outFile.write('</returnStatement>\n')
        return

    def compileDo(self):
        """
        Compiles a do statement
        :return:
        """
        self.eat('do')
        if self.myToken.tokenType() == 'identifier':
            funcName = self.myToken.identifier()
            self.eat()

        if self.myToken.symbol() == '(':
            self.eat('(')
            count = self.CompileExpressionList()
            self.eat(')')
        else:
            self.eat('.')
            if funcName in self.subTable:
                k = self.subTable.getKind(funcName)
                i = self.subTable.getIndex(funcName)
            elif funcName in self.classTable:
                k = self.classTable.getKind(funcName)
                i = self.classTable.getIndex(funcName)
            self.VM.writePush(k, i)
            funcName = self.myToken.identifier()
            self.eat()
            self.eat('(')
            count = self.CompileExpressionList()
            self.eat(')')
            self.VM.writeCall(funcName, count + 1)
        self.eat(';')
        self.VM.writePOP('temp', 0)
        return

    def compileLet(self):
        """
         Compiles a let statement
        """
        self.eat('let')
        name = self.myToken.identifier()
        if name in self.subTable:
            key = self.subTable.getKind(name)
            i = self.subTable.getIndex(name)
        elif name in self.classTable:
            key = self.classTable.getKind(name)
            i = self.classTable.getIndex(name)
        self.VM.writePush(key, i)
        if (self.myToken.symbol() == '['):
            self.eat('[')
            self.CompileExpression()
            self.VM.writeArithmetic('add')
            self.eat(']')
        self.VM.writePOP('pointer', 1)
        self.eat('=')
        self.CompileExpression()
        self.VM.writePOP('that', 0)
        self.eat(';')
        return

    def compileWhile(self):
        """
        Compiles a while statement
        """
        self.eat('while')
        self.eat('(')
        self.CompileExpression()
        self.eat(')')
        self.eat('{')
        self.outFile.write('<statements>\n')
        self.compileStatements()
        self.outFile.write('</statements>\n')
        self.eat('}')
        return

    def compileReturn(self):
        """
        compiles a return statement.
        """
        self.eat('return')
        if self.myToken.tokenType() != 'symbol':
            self.CompileExpression()
        self.eat(';')
        return

    def compileIf(self):
        """
        compiles a if statement.
        """
        l1 = "L" + str(self.label_count)
        l2 = "L" + str(self.label_count + 1)
        self.label_count += LABELS_IN_IF_IMPLEMENTATION
        self.eat('if')
        self.eat('(')
        self.CompileExpression()
        self.eat(')')
        self.VM.writeArithmetic('not')
        self.VM.writeIf("L" + l1)
        self.eat('{')
        # self.outFile.write('<statements>\n')
        self.compileStatements()
        # self.outFile.write('</statements>\n')
        self.eat('}')
        self.VM.writeGoto(l2)
        self.VM.writeLabel(l1)
        if self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() == 'else':
            self.eat('else')
            self.eat('{')
            self.outFile.write('<statements>\n')
            self.compileStatements()
            self.outFile.write('</statements>\n')
            self.eat('}')
            self.VM.writeLabel(l2)
        return

    def CompileExpression(self):
        """
        compiles an expression
        """
        self.CompileTerm()
        while( self.myToken.symbol() in self.operations ):
            op = self.myToken.symbol()
            self.eat() #eating operation
            self.CompileTerm()
            if op in self.opDic:
                self.VM.writeArithmetic(op)
            elif op =='*':
                self.VM.writeCall('Math.multiply', 2)
            elif op == '/':
                self.VM.writeCall('Math.divide', 2)
        self.outFile.write('</expression>\n')

    def CompileTerm(self):
        """
         compiles a term.
        """
        self.outFile.write('<term>\n')
        if self.myToken.tokenType() == 'integerConstant':
            self.VM.writePush('const', self.myToken.intVal())
            self.eat()
        elif self.myToken.tokenType() == 'stringConstant':
            self.VM.writePush('const', self.myToken.stringVal)
            self.eat()
        elif self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() in self.keywordConst:
            self.eat()
        elif self.myToken.tokenType() == 'identifier':
            name = self.myToken.identifier()
            if name in self.subTable:
                self.VM.writePush(self.subTable.getKind(name), self.subTable.getIndex(name))
            elif name in self.classTable:
                self.VM.writePush(self.classTable.getKind(name), self.classTable.getIndex(name))
            self.eat()
            if self.myToken.tokenType() == 'symbol' and self.myToken.symbol() == '[':
                self.eat('[')
                self.CompileExpression()
                self.VM.writeArithmetic('add')
                self.eat(']')
            elif self.myToken.tokenType() == 'symbol' and self.myToken.symbol() == '(':
                self.eat('(')
                self.CompileExpressionList()
                self.eat(')')
            elif self.myToken.tokenType() == 'symbol' and self.myToken.symbol() == '.':
                self.eat('.')
                self.eat()
                self.eat('(')
                self.CompileExpressionList()
                self.eat(')')
        elif self.myToken.tokenType() == 'symbol':
            if self.myToken.symbol() == '(':
                self.eat('(')
                self.CompileExpression()
                self.eat(')')
            else:
                self.eat() #unaryOp or .
                self.CompileTerm()
        self.outFile.write('</term>\n')
        return

    def CompileExpressionList(self):
        """
         compiles a (possibly empty) commaseparated list of expressions.
        """
        count = 0
        if (self.myToken.tokenType() != 'symbol' or self.myToken.symbol() != ')'):
            self.CompileExpression()
            count += 1
        while (self.myToken.symbol() != ')'):
            self.eat(',')
            self.CompileExpression()
            count += 1
        self.outFile.write('</expressionList>\n')
        return count

    def eat(self, string = ''):
        """
        eat a string if we expect something - function will check
        else it will just write the token into an output file
        and get a next token
        :param string:
        :return:
        """
        if self.myToken.tokenType() == 'keyword':
            if string != '' and string != self.myToken.keyWord():
                print('expected ' + string + ' got '+ self.myToken.keyWord())
                return
            self.write(self.myToken.keyWord())
        elif self.myToken.tokenType() == 'symbol':
            if string != '' and string != self.myToken.symbol():
                print('expected ' + string + ', got ' + self.myToken.symbol())
                return
            self.write(self.myToken.symbol())
        elif self.myToken.tokenType() == 'integerConstant':
            self.write(str(self.myToken.intVal()))
        elif self.myToken.tokenType() == 'stringConstant':
            self.write(self.myToken.stringVal())
        elif self.myToken.tokenType() == 'identifier':
            self.write(self.myToken.identifier())
        self.myToken.advance()
        return


    def write(self, word):
        self.outFile.write('<'+self.myToken.tokenType()+'> ')
        word = word.replace('&', '&amp;')
        word = word.replace('<', '&lt;')
        word = word.replace('>', '&gt;')
        self.outFile.write(word)
        self.outFile.write(' </' + self.myToken.tokenType() + '>\n')

    def ifClassVarDec(self):
        if (self.myToken.keyWord() == 'static' or self.myToken.keyWord() == 'field'):
            return True
        return False
