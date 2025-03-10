import paramiko
from io import StringIO
from src.ParamikoMock.ssh_mock import SSHClientMock, SSHCommandMock, SSHMockEnvron, SSHCommandFunctionMock
from src.ParamikoMock.sftp_mock import SFTPClientMock, SFTPFileMock 
from unittest.mock import patch

# Functions below are examples of what an application could look like
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

# Actual tests
# -- This ensures that the ParamikoMock is working as expected
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