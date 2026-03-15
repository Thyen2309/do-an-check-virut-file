#!/usr/bin/env python3
"""Setup script for File Security Checker"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='file-security-checker',
    version='1.0.0',
    description='A local file security analysis tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Security Team',
    author_email='security@example.com',
    url='https://github.com/example/file-security-checker',
    license='MIT',
    
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    python_requires='>=3.9',
    
    install_requires=[
        'python-magic==0.4.27',
        'python-magic-bin==0.4.14',
        'pandas==2.0.3',
        'python-dotenv==1.0.0',
    ],
    
    extras_require={
        'dev': [
            'pytest==7.4.0',
            'pytest-cov==4.1.0',
            'pylint==2.17.5',
            'black==23.7.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'file-security-checker=main:main',
            'fsc-gui=gui:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
