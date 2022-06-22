class FileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.open_file()

    def open_file(self):
        self.file = open(self.file_path, 'r')

    def get_line(self):
        line = self.file.readline()
        if line == '':
            return None
        else:
            yield line
        yield from self.get_line()

    def close_file(self):
        self.file.close()
