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

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.current_file_line = ''
        self.file = None
        self._openFile()

        self.definitions = []
        self.events = []
        self.current_line = None
        self._parseDefinitions()

    def _openFile(self):
        self.file = open(self.file_path, 'r')

    def _getLine(self):
        self.current_line = self.file.readline()
        if self.current_line == '':
            return None
        else:
            return self.current_line

    def _getDefinitons(self):
        result = []
        line = self._getLine()
        while line != None:
            self.current_line = line
            if line.startswith("%"):
                result.append(line)
            else:
                break
            line = self._getLine()
        self.definitions = PajeParser.definitionGenerator(result)

    def _parseDefinitions(self):
        self._getDefinitons()
        for definition in self.definitions:
            pass

    def getEvent(self):
        result = self.current_line
        line = self._getLine()
        if line != None:
            self.current_line = line
        else:
            self.current_line = None
        return result
