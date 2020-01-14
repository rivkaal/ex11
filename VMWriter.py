class VMWriter:
    TRUE = -1
    FALSE = 0
    NULL = 0

    def __init__(self, file_path):
        self.out_file = open(file_path, 'w')

    def writePush(self, segment, index):
        if index < 0:
            self.out_file.write("push " + segment + " " + str(0) + '\n')
            self.out_file.write('not \n')
        else:
            self.out_file.write("push " + segment + " " + str(index) + '\n')

    def writePOP(self, segment, index):
        self.out_file.write("pop " + segment + " " + str(index) + '\n')

    def writeArithmetic(self, command):
        self.out_file.write(command + '\n')

    def writeLabel(self, label):
        self.out_file.write("label " + label + '\n')

    def writeGoto(self, label):
        self.out_file.write("goto " + label + '\n')

    def writeIf(self, label):
        self.out_file.write("if-goto " + label + '\n')

    def writeCall(self, name, nArgs):
        self.out_file.write("call " + name + " " + str(nArgs)+'\n')

    def writeFunction(self, name, nLocals):     # TODO what about constructor?
        self.out_file.write("function " + name + " " + str(nLocals)+'\n')

    def writeReturn(self):
        self.out_file.write("return" + '\n')

    def close(self):
        self.out_file.close()
