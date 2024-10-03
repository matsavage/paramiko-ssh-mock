from abc import abstractmethod, ABC
from io import StringIO
import re
from paramiko.ssh_exception import BadHostKeyException, NoValidConnectionsError

# Singleton
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

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

class SSHClientMock():
    sftp_client_mock = SFTPClientMock()
    called = []
    def __init__(self, *args, **kwds):
        self.selected_host = None
        self.command_responses = {}
    
    def load_system_host_keys(self):
        pass
    
    def set_missing_host_key_policy(self, policy):
        pass

    def open_sftp(self):
        return self.sftp_client_mock
    
    def connect(self, host, port, username, password, banner_timeout):
        self.selected_host = f'{host}:{port}'
        if self.selected_host not in SSHMockEnvron().commands_response:
            raise BadHostKeyException(host, None, 'No valid responses for this host')
        set_credentials = SSHMockEnvron().router_credentials.get(self.selected_host)
        if set_credentials is not None:
            if set_credentials != (username, password):
                raise BadHostKeyException(host, None, 'Invalid credentials')
        self.command_responses = SSHMockEnvron().commands_response[self.selected_host]
        self.clear_called_commands()

    def clear_called_commands(self):
        self.called.clear()
    
    def exec_command(self, command):
        if self.selected_host is None:
            raise NoValidConnectionsError('No valid connections')
        self.called.append(command)
        response = self.command_responses.get(command)
        if response is None:
            # check if there is a command that can be used as regexp
            for command_key in self.command_responses:
                if command_key.startswith('re(') and command_key.endswith(')'):
                    regexp_exp = command_key[3:-1]
                    if re.match(regexp_exp, command):
                        response = self.command_responses[command_key]
                        break
            if response is None:
                raise NotImplementedError('No valid response for this command')
        return response(self, command)
    
    def close(self):
        self.selected_commands = None
        self.command_responses = {}

class SSHResponseMock(ABC):
    @abstractmethod
    def __call__(self, ssh_client_mock: SSHClientMock, command:str):
        pass

class SSHMockEnvron(metaclass=SingletonMeta):
    def __init__(self):
        self.commands_response = {}
        self.router_credentials = {}
    
    def add_responses_for_host(self, host, port, responses: dict[str, SSHResponseMock], username=None, password=None):
        self.commands_response[f'{host}:{port}'] = responses
        if username and password:
            self.router_credentials[f'{host}:{port}'] = (username, password)
    
    def cleanup_environment(self):
        self.commands_response = {}

class SSHCommandMock(SSHResponseMock):
    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, ssh_client_mock: SSHClientMock, command:str) -> tuple[StringIO, StringIO, StringIO]:
        return StringIO(self.stdin), StringIO(self.stdout), StringIO(self.stderr)

    def append_to_stdout(self, new_stdout):
        self.stdout += new_stdout
    
    def remove_line_containing(self, line):
        self.stdout = '\n'.join([x for x in self.stdout.split('\n') if line not in x])

class SSHCommandFunctionMock(SSHResponseMock):
    def __init__(self, callback):
        self.callback = callback
    
    def __call__(self, ssh_client_mock: SSHClientMock, command:str) -> tuple[StringIO, StringIO, StringIO]:
        return self.callback(ssh_client_mock, command)
