from distutils.core import setup

setup(
    name='bot2',
    version='',
    packages=['PythonApi', 'PythonApi.Base', 'PythonApi.RPApi',
     'PythonApi.tests', 'PythonApi.jotihunt',
     'PythonApi.jotihunt2', 'PythonApi.scraperApi'],
    url='',
    license='',
    author='mattijn',
    author_email='',
    description='', requires=['requests', 'pyorient',
     'python-telegram-bot']
)
