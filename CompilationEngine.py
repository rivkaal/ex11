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
LABELS_IN_WHILE_IMPLEMENTATION = 2

#hey!!!
#,kermlk
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
            self.className = self.myToken.identifier()
            self.eat()
        if self.myToken.tokenType() == 'symbol':
            self.eat('{')
        if self.myToken.tokenType() == 'keyword':
            if self.ifClassVarDec():
                while(self.ifClassVarDec()):
                    self.CompileClassVarDec()
            while(self.myToken.keyWord() in self.subDecList):
                if self.myToken.keyWord() == 'method':
                    self.subTable.define('this', self.className, 'argument')
                self.CompileSubroutine()
        self.eat('}')
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
        count = 0
        ifMethod = False
        self.subTable.startSubroutine()
        if self.myToken.tokenType() == 'keyword':
            self.eat()
        if self.myToken.tokenType() =='keyword':
            if self.myToken.keyWord() not in self.classVarTypes:
                self.eat('void')
            else:
                if self.myToken.keyWord() == 'method':
                    ifMethod = True
                    count += 1
                    self.subTable.define('this', self.className, 'argument')
                self.eat()
        elif self.myToken.tokenType() == 'identifier':
            self.eat()
        else : print('expected something else')
        if self.myToken.tokenType() == 'identifier':
            name  = self.myToken.identifier()
            self.eat()
        else: print('expected something else')
        self.eat('(')
        count += self.compileParameterList()
        self.eat(')')
        self.VM.writeFunction((self.className + '.'+name), count)
        self.eat('{')
        if (self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() == 'var'):
            while (self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() == 'var'):
                self.compileVarDec()
        if ifMethod:
            self.VM.writePush('argument', 0)
            self.VM.writePOP('pointer', 0)
        self.compileStatements()
        self.eat('}')




        return

    def compileParameterList(self):
        """
        compiles a (possibly empty) parameter list, not including the enclosing "()".
        :return:
        """
        if self.myToken.tokenType() == 'symbol' and self.myToken.symbol() == ')':
            return 0
        count = 0
        while (self.myToken.tokenType() != 'symbol' or self.myToken.symbol() != ')'):
            count += 1
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
        return count

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
                self.compileLet()
            elif self.myToken.keyWord() == 'if':
                self.compileIf()
            elif self.myToken.keyWord() == 'while':
                self.compileWhile()
            elif self.myToken.keyWord() == 'do':
                self.compileDo()
            elif self.myToken.keyWord() == 'return':
                self.compileReturn()
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
                self.VM.writePush(k, i)
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
        self.eat()
        if (self.myToken.symbol() == '['):
            self.eat('[')
            self.VM.writePush(key, i)
            self.CompileExpression()
            self.VM.writeArithmetic('add')
            self.eat(']')
            self.VM.writePOP('pointer', 1)
            key = 'that'
            i = 0
        self.eat('=')
        self.CompileExpression()
        self.VM.writePOP(key, i)
        self.eat(';')
        return

    def compileCall(self):
        if self.myToken.tokenType() == 'identifier':
            name = self.myToken.identifier()
            self.eat()

        if self.myToken.symbol() == '(':
            self.eat('(')
            count = self.CompileExpressionList()
            self.eat(')')
        else:
            self.eat('.')
            count = 0
            if name in self.subTable:
                className = self.subTable.getKind(name)
                i = self.subTable.getIndex(name)
                count += 1
                self.VM.writePush('pointer', 0)
            elif name in self.classTable:
                className = self.classTable.getKind(name)
                i = self.classTable.getIndex(name)
                count += 1
                self.VM.writePush('pointer', 0)
            else:
                className = name
                name = self.myToken.identifier()
            self.eat()
            self.eat('(')
            count += self.CompileExpressionList()
            self.eat(')')
        self.VM.writeCall((className+'.'+name), count)
        self.eat(';')
        self.VM.writePOP('temp', 0)
        return

    def compileWhile(self):
        """
        Compiles a while statement
        """
        l1 = "L" + str(self.label_count)
        l2 = "L" + str(self.label_count + 1)
        self.label_count += LABELS_IN_WHILE_IMPLEMENTATION
        self.VM.writeLabel(l1)
        self.eat('while')
        self.eat('(')
        self.CompileExpression()
        self.eat(')')
        self.VM.writeArithmetic('not')
        self.VM.writeIf(l2)

        self.eat('{')
        self.compileStatements()
        self.eat('}')
        self.VM.writeGoto(l1)
        self.VM.writeLabel(l2)
        return

    def compileReturn(self):
        """
        compiles a return statement.
        """
        self.eat('return')
        if self.myToken.tokenType() != 'symbol':
            self.CompileExpression()
        else:
            self.VM.writePush('constant', 0)
        self.eat(';')
        self.VM.writeReturn()
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
        self.compileStatements()
        self.eat('}')
        self.VM.writeGoto(l2)
        self.VM.writeLabel(l1)
        if self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() == 'else':
            self.eat('else')
            self.eat('{')
            self.compileStatements()
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
                self.VM.writeArithmetic(self.opDic[op])
            elif op =='*':
                self.VM.writeCall('Math.multiply', 2)
            elif op == '/':
                self.VM.writeCall('Math.divide', 2)

    def CompileTerm(self):
        """
         compiles a term.
        """
        if self.myToken.tokenType() == 'integerConstant':
            self.VM.writePush('constant', self.myToken.intVal())
            self.eat()
        elif self.myToken.tokenType() == 'stringConstant':
            self.handle_string(self.myToken.stringVal())
            self.eat()
        elif self.myToken.tokenType() == 'keyword' and self.myToken.keyWord() in self.keywordConst:
            self.VM.writePush('constant', self.getConstValue(self.myToken.keyWord()))
            self.eat()
        elif self.myToken.tokenType() == 'identifier':
            name = self.myToken.identifier()
            if name in self.subTable:
                namefull = self.subTable.getKind(name)
                self.VM.writePush(namefull, self.subTable.getIndex(name))
            elif name in self.classTable:
                namefull = self.classTable.getKind(name)
                self.VM.writePush(namefull, self.classTable.getIndex(name))
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
                funcName = self.myToken.identifier()
                self.eat()
                self.eat('(')
                count = self.CompileExpressionList()
                self.eat(')')
                self.VM.writeFunction(name + '.'+funcName, count)
        elif self.myToken.tokenType() == 'symbol':
            if self.myToken.symbol() == '(':
                self.eat('(')
                self.CompileExpression()
                self.eat(')')
            else:
                self.eat() #unaryOp or .
                self.CompileTerm()
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
        pass

    def ifClassVarDec(self):
        if (self.myToken.keyWord() == 'static' or self.myToken.keyWord() == 'field'):
            return True
        return False


    def getConstValue(self,val):
        if val == "true":
            return -1
        else:
            return 0

    def handle_string(self, term):
        """
        Handle translation of a string object
        :param term: term that contains the string
        :return:
        """
        self.VM.writePush('constant', len(term))
        self.VM.writeFunction('String.new', 1)
        for char in term:
            self.VM.writePush('constant', ord(char))
            self.VM.writeFunction('String.appendChar', 2)
        return
