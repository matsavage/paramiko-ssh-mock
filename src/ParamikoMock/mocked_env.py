from .metaclasses import SingletonMeta
from .exceptions import BadSetupError

from .sftp_mock import SFTPFileSystem, SFTPFileMock
from .local_filesystem_mock import LocalFileMock, LocalFilesystemMock

# Import only for type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ssh_mock import SSHResponseMock, SSHClientMock

class MockRemoteDevice:
    def __init__(self, host, port, responses: dict[str, 'SSHResponseMock'], local_filesystem, username=None, password=None):
        self.host = host
        self.port = port
        self.responses = responses
        self.username = username
        self.password = password
        self.filesystem = SFTPFileSystem()
        self.local_filesystem = local_filesystem
        self.command_history = []
    
    def authenticate(self, username, password):
        if self.username is None and self.password is None:
            return True
        return (self.username, self.password) == (username, password)
    
    def clear(self):
        self.command_history.clear()
    
    def add_command_to_history(self, command):
        self.command_history.append(command)

# ParamikoMockEnviron is a Singleton class that stores the responses for the SSHClientMock
class ParamikoMockEnviron(metaclass=SingletonMeta):
    def __init__(self):
        self.__remote_devices__: dict[str, 'MockRemoteDevice'] = {}
        # Local filesystem
        self.__local_filesystem__: "LocalFilesystemMock" = LocalFilesystemMock()
    
    # Private/protected methods
    def _get_remote_device(self, host):
        return self.__remote_devices__.get(host) or (_ for _ in ()).throw(BadSetupError('Remote device not registered, did you forget to call add_responses_for_host?'))
    
    # Public methods
    def add_responses_for_host(self, host, port, responses: dict[str, 'SSHResponseMock'], username=None, password=None):
        self.__remote_devices__[f'{host}:{port}'] = MockRemoteDevice(
            host, port, responses, self.__local_filesystem__, 
            username, password
        )
    
    def cleanup_environment(self):
        # Clear all the responses, credentials and filesystems
        self.__remote_devices__.clear()
        self.__local_filesystem__.file_system.clear()        
    
    def add_mock_file_for_host(self, host, port, path, file_mock:'SFTPFileMock'):
        device = self._get_remote_device(f'{host}:{port}')
        device.filesystem.add_file(path, file_mock)
    
    def remove_mock_file_for_host(self, host, port, path):
        device = self._get_remote_device(f'{host}:{port}')
        device.filesystem.remove_file(path)
    
    def get_mock_file_for_host(self, host, port, path):
        device = self._get_remote_device(f'{host}:{port}')
        return device.filesystem.get_file(path)
    
    # Asserts
    def assert_command_was_executed(self, host, port, command):
        device = self._get_remote_device(f'{host}:{port}')
        assert command in device.command_history
    
    def assert_command_was_not_executed(self, host, port, command):
        device = self._get_remote_device(f'{host}:{port}')
        assert command not in device.command_history
    
    def assert_command_executed_on_index(self, host, port, command, index):
        device = self._get_remote_device(f'{host}:{port}')
        assert device.command_history[index] == command