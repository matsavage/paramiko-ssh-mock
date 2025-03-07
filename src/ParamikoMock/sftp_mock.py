import time
import os
from paramiko import SFTPAttributes

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
