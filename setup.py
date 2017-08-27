import os
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('cleverbot/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

with open('README.rst') as f:
    readme = f.read()

setup(
    name='cleverbot.py',
    version=version,
    description='A Cleverbot API wrapper for Python with asynchronous '
    'functionality.',
    long_description=readme,
    url='https://github.com/orlnub123/cleverbot.py',
    author='orlnub123',
    license='MIT',
    packages=['cleverbot'],
    install_requires=['requests>=1.0.0'],
    extras_require={'async': ['aiohttp>=1.0.0']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
