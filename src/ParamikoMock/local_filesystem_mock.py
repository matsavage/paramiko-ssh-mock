# SFTPFileSystem is a class that stores the file system for the SFTPClientMock
class LocalFilesystemMock():
    file_system: dict[str, "LocalFileMock"] = {}

    def add_file(self, path, content):
        self.file_system[path] = content

    def get_file(self, path):
        return self.file_system.get(path)
    
    def remove_file(self, path):
        self.file_system.pop(path, None)

class LocalFileMock():
    write_history = []
    file_content = None

    def close(self):
        pass

    def write(self, data):
        self.write_history.append(data)
        self.file_content = data
    
    def read(self, size=None):
        return self.file_content

