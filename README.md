# ParamikoMock

ParamikoMock is a Python library for mocking the `paramiko` SSH client for testing purposes. It allows you to define responses for specific SSH commands and hosts, making it easier to test code that interacts with remote servers via SSH. 

## Installation

```bash
pip install paramiko-mock
```

## Usage

Here are some examples of how to use ParamikoMock:

### Example 1

This example shows how to mock an SSH connection to a host named `some_host` on port `22`. The `ls -l` command is mocked to return the string `'ls output'`.

```python
from ParamikoMock import SSHMockEnvron, SSHCommandMock
from unittest.mock import patch
import paramiko

def example_function_1():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('some_host', port=22, username='root', password='root', banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('ls -l')
    return stdout.read()

def test_example_function_1():
    SSHMockEnvron().add_responses_for_host('some_host', 22, {
        'ls -l': SSHCommandMock('', 'ls output', '')
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_1()
        assert output == 'ls output'
```

### Example 2

This example shows how to mock an SSH connection to a host named `some_host_2` on port `4826`. The `sudo docker ps` command is mocked to return the string `'docker-ps-output'`.

```python
from ParamikoMock import SSHMockEnvron, SSHCommandMock
from unittest.mock import patch
import paramiko

def example_function_2():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('some_host_2', port=4826, username='root', password='root', banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('sudo docker ps')
    return stdout.read()

def test_example_function_2():
    SSHMockEnvron().add_responses_for_host('some_host_2', 4826, {
        'sudo docker ps': SSHCommandMock('', 'docker-ps-output', '')
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_2()
        assert output == 'docker-ps-output'
```

### Example 3

This example shows how to mock an SSH connection to a host named `some_host_3` on port `22`. The `custom_command --param1 value1` command is mocked to return the string `'value1'`.

```python
from ParamikoMock import SSHMockEnvron, SSHCommandFunctionMock
from unittest.mock import patch
import paramiko

def example_function_3():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('some_host_3', port=22, username='root', password='root', banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('custom_command --param1 value1')
    return stdout.read()

def test_example_function_3():
    def custom_command_processor(ssh_client_mock: SSHClientMock, command: str):
        if 'param1' in command and 'value1' in command:
            return StringIO(''), StringIO('value1'), StringIO('')
    
    SSHMockEnvron().add_responses_for_host('some_host_3', 22, {
        r're(custom_command .*)': SSHCommandFunctionMock(custom_command_processor)
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_3()
        assert output == 'value1'
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

[Github](https://github.com/ghhwer/paramiko-ssh-mock)

## License

[MIT](https://choosealicense.com/licenses/mit/) 