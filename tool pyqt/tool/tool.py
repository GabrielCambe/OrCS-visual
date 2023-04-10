import sys
from PyQt5 import QtWidgets

from Window import WindoWidget


#TODO: pesquisar artgos sobre visualização de arquiteturas em software
#TODO: iniciar rascunho do TCC no sharelatex, utilizando os picotes que você já escreveu

class FileReader():
    @staticmethod
    def lineGenerator(fileReader):
        line = fileReader.get_line() 
        yield line
        if line == None:
            return
        else:
            yield from FileReader.lineGenerator(fileReader)


    def __init__(self, file_path):
        self.file_path = file_path
        self.current_line = ''
        self.open_file()
        self.lines = FileReader.lineGenerator(self)

    def open_file(self):
        self.file = open(self.file_path, 'r')

    def get_line(self):
        self.current_line = self.file.readline()
        if self.current_line == '':
            return None
        else:
            return self.current_line

    def close_file(self):
        self.file.close()


class PajeParser():
    @staticmethod
    def definitionGenerator(definitions):
        if len(definitions) == 0:
            return
        result = [definitions.pop(0)]
        while result[-1] != "%EndEventDef\n":
            result.append(definitions.pop(0))
        yield result
        if len(result) == 0:
            return
        else:
            yield from PajeParser.definitionGenerator(definitions)

    @staticmethod
    def eventGenerator(events):
        if len(events) == 0:
            return
        yield events.pop(0)
        yield from PajeParser.definitionGenerator(events)


    def __init__(self, fileReader) -> None:
        self.mode = 'EVENT'
        # self.mode = 'CYCLE'
        self.fileReader = fileReader
        self.definitions = []
        self.events = []
        self.current_line = None
        self.parseDefinitions()
    
    def _getDefinitons(self):
        result = []
        for line in self.fileReader.lines:
            self.current_line = line
            if line.startswith("%"):
                result.append(line)
            else:
                break
        self.definitions = PajeParser.definitionGenerator(result)

    def getEvent(self):
        result = self.current_line
        for line in self.fileReader.lines:
            self.current_line = line
            break
        return result

    def parseDefinitions(self):
        self._getDefinitons()
        for definition in self.definitions:
            pass
            # print(definition)
        # for events in self.file



if __name__ == "__main__":
    # fileReader = FileReader("/home/gabriel/Documents/OrCS-visual/pajeEvents")
    fileReader = FileReader("/home/gabriel/Documentos/HiPES/OrCS-visual/pajeEvents")
    parser = PajeParser(fileReader)

    app = QtWidgets.QApplication(sys.argv)
    window = WindoWidget(title='OrCS-visual', parser=parser)
    window.showMaximized()
    sys.exit(app.exec_())
