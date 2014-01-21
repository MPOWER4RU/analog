"""Analog - Log Analysis Utitliy."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from setuptools import setup, find_packages
import sys


def read(path, strip=False):
    """Read file at ``path`` and return content. Opt., ``strip`` whitespace."""
    content = ''
    with open(path) as fp:
        content = fp.read()
        if strip:
            content = content.strip()
    return content


classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: Log Analysis',
    'Topic :: System :: Logging',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    'Topic :: Utilities',
    'Programming Language :: Python :: 3'] + [
    'Programming Language :: Python :: {0}'.format(pyv)
    for pyv in "2.6 2.7 3.0 3.1 3.2 3.3".split()
]


PYMAJ = sys.version_info[0]
PYMIN = sys.version_info[1]

requirements = ['tabulate']
# mock required for Python <= 3.3 (else unittest.mock)
if PYMAJ < 3 or (PYMAJ == 3 and PYMIN < 3):
    requirements.append('mock')
# numpy required for Python <= 3.4 (else statistics)
if PYMAJ < 3 or (PYMAJ == 3 and PYMIN < 4):
    requirements.append('numpy')


setup(
    name='analog',
    description='analog - Log Analysis Utility',
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    version=read('VERSION'),
    url='https://bitbucket.org/fabianbuechler/analog',
    license='MIT license',
    author='Fabian Büchler',
    author_email='fabian.buechler@gmail.com',
    entry_points={'console_scripts': ['analog=analog:main']},
    classifiers=classifiers,
    install_requires=requirements,
    packages=find_packages(),
    py_modules=['analog'],
    zip_safe=False,
)
