from setuptools import find_packages
from setuptools import setup

setup(
    name='importsorcery',
    version='0.1',
    packages=find_packages(),
    zip_safe=False,
    entry_points = {
        'console_scripts': ['importsorcery=importsorcery:main'],
    },
)
