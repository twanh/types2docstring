from setuptools import find_packages
from setuptools import setup

setup(
    name='types2docstring',
    version='0.0.0',
    description='Automatically generates a docstring for type annotated functions.',  # noqa: E501
    url='https://github.com/twanh/types2docstring',
    author='twanh',
    author_email='huiskenstwan@gmail.com',
    packages=find_packages(exclude=('tests',)),
    python_requires='>=3.9.2',
    install_requires=[
        'tokenize-rt>=4.2.1',
    ],
    entry_points={
        'console_scripts': [
            'types2docstring=types2docstring.__main__:run',
        ],
    },
)
