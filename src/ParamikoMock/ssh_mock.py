from abc import abstractmethod, ABC
from io import StringIO
import re
from paramiko.ssh_exception import BadHostKeyException, NoValidConnectionsError
from .sftp_mock import SFTPClientMock
from .metaclasses import SingletonMeta
from .exceptions import BadSetupError

# SSHMockEnvron is a Singleton class that stores the responses for the SSHClientMock
class SSHMockEnvron(metaclass=SingletonMeta):
    def __init__(self):
        self.__commands_response__ = {}
        self.__device_credentials__ = {}
    
    def add_responses_for_host(self, host, port, responses: dict[str, 'SSHResponseMock'], username=None, password=None):
        self.__commands_response__[f'{host}:{port}'] = responses
        if username and password:
            self.__device_credentials__[f'{host}:{port}'] = (username, password)
    
    def cleanup_environment(self):
        self.__commands_response__ = {}
    
    def get_credentials_for_host(self, host):
        return self.__device_credentials__.get(host) or (_ for _ in ()).throw(BadSetupError('No credentials set for this host'))

    def get_command_response_for_host(self, host):
        return self.__commands_response__.get(host) or (_ for _ in ()).throw(BadSetupError('No responses set for this host'))

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
    
    def set_log_channel(self, log_channel):
        pass
    
    def get_host_keys(self):
        pass
    
    def save_host_keys(self, filename):
        pass
    
    def load_host_keys(self, filename):
        pass
    
    def load_system_host_keys(self, filename=None):
        pass
    
    def connect(
        self, hostname, 
        port=22, username=None, password=None, 
        **kwargs
    ):
        self.selected_host = f'{hostname}:{port}'
        self.command_responses = SSHMockEnvron().get_command_response_for_host(self.selected_host)
        set_credentials = SSHMockEnvron().get_credentials_for_host(self.selected_host)
        if set_credentials is not None:
            if set_credentials != (username, password):
                raise BadHostKeyException(hostname, None, 'Invalid credentials')
        
        self.last_connect_kwargs = kwargs
        self.clear_called_commands()

    def clear_called_commands(self):
        self.called.clear()
    
    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False, environment=None):
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
    
    def invoke_shell(self, term='vt100', width=80, height=24, width_pixels=0, height_pixels=0, environment=None):
        pass
    
    def close(self):
        self.selected_commands = None
        self.command_responses = {}

    def get_called_commands(self):
        return self.called
    
    def assert_command_was_called(self, command):
        assert command in self.called  
    
    def assert_command_called_on_index(self, index, command):
        if len(self.called) <= index:
            raise AssertionError(f'Command was not called on index {index}')
        assert self.called[index] == command

class SSHResponseMock(ABC):
    @abstractmethod
    def __call__(self, ssh_client_mock: SSHClientMock, command:str):
        pass

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
