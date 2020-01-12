import os
import sys
import Tokenizer as T
import CompilationEngine as CE


class JackAnalyzer:

    def __init__(self, file_path):
        self.jackFiles = []

        if os.path.isdir(file_path):
            for file in os.listdir(file_path):
                if file.endswith(".jack"):
                    self.jackFiles.append(file_path + os.sep + file)

        else:
            if file_path.endswith(".jack"):
                self.jackFiles.append(file_path)

    def analyze(self):
        for jack_file in self.jackFiles:
            tokenizer = T.Tokenizer(jack_file)
            xml_file = jack_file.replace('.jack', '.xml')
            comp_engine = CE.Parsing(tokenizer, xml_file)
            comp_engine.outFile.close()
            tokenizer.close()


if __name__ == '__main__':
    JackAnalyzer = JackAnalyzer(sys.argv[1])
    JackAnalyzer.analyze()
