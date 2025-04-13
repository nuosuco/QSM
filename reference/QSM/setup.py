"""
量子基因编码: QG-QSM01-CODE-20250401213403-23BABF-ENT8591
"""

from setuptools import setup, find_packages

setup(
    name="QSM",
    version="0.1",
    packages=find_packages(),
    install_requires=open('requirements.txt', encoding='utf-8').read().splitlines(),
    entry_points={
        'console_scripts': [
            'qsm=flask_api:app.run'
        ]
    }
)