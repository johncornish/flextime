from setuptools import setup, find_packages

setup(
    name='flextime',
    version='0.1',
    py_modules=['flextime'],
    install_requires=[
        'click',
        'python-dateutil',
        'PyYAML',
        'networkx',
        'pytest',
    ],
    entry_points='''
    [console_scripts]
    ft=flextime:cli
    ''',
)
