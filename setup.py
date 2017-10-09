from setuptools import setup

setup(
    name='flextime',
    version='0.1',
    py_modules=['flextime'],
    install_requires=[
        'click',
        'python-dateutil',
        'PyYAML',
    ],
    entry_points='''
    [console_scripts]
    ft=main:cli
    ''',
)
