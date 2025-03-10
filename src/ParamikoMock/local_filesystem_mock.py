# SFTPFileSystem is a class that stores the file system for the SFTPClientMock
class LocalFilesystemMock():
    file_system: dict[str, "LocalFileMock"] = {}

    def add_file(self, path:str, file_mock:"LocalFileMock"):
        self.file_system[path] = file_mock

    def get_file(self, path):
        return self.file_system.get(path)
    
    def remove_file(self, path):
        self.file_system.pop(path, None)

class LocalFileMock():
    write_history = []
    file_content = None

