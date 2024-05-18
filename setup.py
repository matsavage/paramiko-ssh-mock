# Setup script for the module 'paramiko-mock' located in the 'src' directory.
# The setup script is used to install the module in the local environment.

from setuptools import setup, find_packages

setup(
    name='paramiko-mock',
    version='0.1.0',
    description='Mock for paramiko library',
    author='Caio Cominato',
    author_email='caiopetrellicominato@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'paramiko>=3.4.0'
    ],
    zip_safe=False
)
