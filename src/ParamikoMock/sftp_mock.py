import time
import os
from paramiko import SFTPAttributes
from .exceptions import BadSetupError

# SFTPFileSystem is a class that stores the file system for the SFTPClientMock
class SFTPFileSystem():
    file_system: dict[str, "SFTPFileMock"] = {}

    def add_file(self, path, content):
        self.file_system[path] = content

    def get_file(self, path):
        return self.file_system.get(path)
    
    def remove_file(self, path):
        self.file_system.pop(path, None)

class SFTPFileMock():
    write_history = []
    file_content = None

    def close(self):
        pass

    def write(self, data):
        self.write_history.append(data)
        self.file_content = data
    
    def read(self, size=None):
        return self.file_content

class SFTPClientMock():
    def __init__(self, file_system:SFTPFileSystem=None, local_filesystem=None):
        if file_system is None:
            raise BadSetupError("file_system is required")
        if local_filesystem is None:
            raise BadSetupError("local_filesystem is required")
        self.__remote_file_system__ = file_system
        self.__local_filesystem__ = local_filesystem
        
    def open(self, filename, mode="r", bufsize=-1):
        file = self.__remote_file_system__.get_file(filename)
        if file is None:
            file = SFTPFileMock()
            self.__remote_file_system__.add_file(filename, file)
        return file
    
    def close(self):
        pass

    def put(self, localpath, remotepath, callback=None, confirm=True):
        # Creating a fake os.stat_result object
        size = len(self.sftp_file_mock.file_content)
        fake_stat = os.stat_result((
            33206,   # st_mode (file mode)
            1234567, # st_ino (inode number)
            1000,    # st_dev (device)
            1,       # st_nlink (number of hard links)
            1001,    # st_uid (user ID of owner)
            1002,    # st_gid (group ID of owner)
            size,    # st_size (size in bytes)
            int(time.time()),  # st_atime (last access time)
            int(time.time()),  # st_mtime (last modification time)
            int(time.time())   # st_ctime (creation time on Windows, metadata change on Unix)
        ))
        if confirm:
            s = SFTPAttributes.from_stat(fake_stat)
            if s.st_size != size:
                raise IOError(
                    "size mismatch in put!  {} != {}".format(s.st_size, size)
                )
        else:
            s = SFTPAttributes()
        return s
