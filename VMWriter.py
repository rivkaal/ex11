class VMWriter:
    TRUE = -1
    FALSE = 0
    NULL = 0

    def __init__(self, file_path):
        self.out_file = open(file_path, 'w')

    def writePush(self, segment, index):
        self.out_file.write("push " + segment + " " + str(index) + '\n')

    def writePOP(self, segment, index):
        self.out_file.write("pop " + segment + " " + str(index) + '\n')

    def writeArithmetic(self, command):
        self.out_file.write(command + '\n')

    def writeLabel(self, label):
        self.out_file.write("label " + label + '\n')

    def writeGoto(self, label):
        self.out_file.write("goto " + label + '\n')

    def writeCall(self, name, nArgs):
        self.out_file.write("call " + name + " " + str(nArgs))

    def writeFunction(self, name, nLocals):     # TODO what about constructor?
        self.out_file.write("function " + name + " " + str(nLocals))

    def writeReturn(self):
        self.out_file.write("return")

    def close(self):
        self.out_file.close()
