class FileReader():
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_line = ''
        self.file = None
        self.open_file()

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

    def __init__(self, file_path) -> None:
        self.fileReader = FileReader(file_path)
        self.definitions = []
        self.events = []
        self.current_line = None
        self.parseDefinitions()
    
    def _getDefinitons(self):
        result = []
        line = self.fileReader.get_line()
        while line != None:
            self.current_line = line
            if line.startswith("%"):
                result.append(line)
            else:
                break
            line = self.fileReader.get_line()
        self.definitions = PajeParser.definitionGenerator(result)

    def getEvent(self):
        result = self.current_line
        line = self.fileReader.get_line()
        if line != None:
            self.current_line = line
        else:
            self.current_line = None
        return result

    def parseDefinitions(self):
        self._getDefinitons()
        for definition in self.definitions:
            pass
            # print(definition)
        # for events in self.file
