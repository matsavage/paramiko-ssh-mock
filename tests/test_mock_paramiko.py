import paramiko
from io import StringIO
from src.ParamikoMock.ssh_mock import SSHClientMock, SSHCommandMock, SSHMockEnvron, SSHCommandFunctionMock, SFTPFileMock
from unittest.mock import patch

def example_function_1():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('ls -l')
    return stdout.read()

def example_function_2():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host_2',
                    port=4826,
                    username='root',
                    password='root',
                    banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('sudo docker ps')
    return stdout.read()

def example_function_3():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host_3',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('custom_command --param1 value1')
    return stdout.read()

def example_function_sftp_write():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host_4',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    # Some example of a remote file write
    sftp = client.open_sftp()
    file = sftp.open('/tmp/afileToWrite.txt', 'w')
    file.write('Something to put in the remote file')
    file.close()
    sftp.close()

def example_function_sftp_read():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host_4',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    # Some example of a remote file write
    sftp = client.open_sftp()
    file = sftp.open('/tmp/afileToRead.txt', 'r')
    output = file.read()
    file.close()
    sftp.close()
    return output

def test_example_function_1():
    SSHMockEnvron().add_responses_for_host('some_host', 22, {
        'ls -l': SSHCommandMock('', 'ls output', '')
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_1()
        assert output == 'ls output'

def test_example_function_2():
    ssh_mock = SSHClientMock()
    SSHMockEnvron().add_responses_for_host('some_host_2', 4826, {
        'sudo docker ps': SSHCommandMock('', 'docker-ps-output', '')
    }, 'root', 'root')
    # patch the paramiko.SSHClient with the mock
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_2()
        assert output == 'docker-ps-output'

def test_example_function_3():
    # We can also use a custom command processor
    def custom_command_processor(ssh_client_mock: SSHClientMock, command: str):
        # Parse the command and do something with it
        if 'param1' in command and 'value1' in command:
            return StringIO(''), StringIO('value1'), StringIO('')
    
    # You can use a regexp expresion to match the command with the custom processor
    ssh_mock = SSHClientMock()
    SSHMockEnvron().add_responses_for_host('some_host_3', 22, {
        r're(custom_command .*)': SSHCommandFunctionMock(custom_command_processor) # This is a regexp command
    }, 'root', 'root')
    # patch the paramiko.SSHClient with the mock
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_3()
        assert output == 'value1'

def test_example_function_sftp_write():
    ssh_mock = SSHClientMock()

    SSHMockEnvron().add_responses_for_host('some_host_4', 22, {
        'ls -l': SSHCommandMock('', 'ls output', '')
    }, 'root', 'root')
    # patch the paramiko.SSHClient with the mock
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        example_function_sftp_write()
        assert 'Something to put in the remote file' == ssh_mock.sftp_client_mock.sftp_file_mock.written[0]

def test_example_function_sftp_read():
    ssh_mock = SSHClientMock()

    SSHMockEnvron().add_responses_for_host('some_host_4', 22, {
        'ls -l': SSHCommandMock('', 'ls output', '')
    }, 'root', 'root')
    ssh_mock.sftp_client_mock.sftp_file_mock.file_content = 'Something from the remote file'
    # patch the paramiko.SSHClient with the mock
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_sftp_read()
        assert 'Something from the remote file' == output