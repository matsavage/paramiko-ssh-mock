class SFTPFileMock():
    written = []
    file_content = None

    def close(self):
        pass

    def write(self, data):
        self.written.append(data)
    
    def read(self, size=None):
        return self.file_content
    

class SFTPClientMock():
    sftp_file_mock = SFTPFileMock()
    def open(self, filename, mode="r", bufsize=-1):
        return self.sftp_file_mock
    
    def close(self):
        pass