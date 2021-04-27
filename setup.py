# -*- coding: utf-8 -*-
#%%
from setuptools import setup

with open('README.md') as readme:
    l_description = readme.read()
with open('requirements.txt') as reqs:
    requirements = reqs.read()

setup(
    name = 'shacl2puml',
    version = '0.0.1',
    packages = ['shacl2puml'],
    description='Shacl diagram generator',
    long_description=l_description,
    author='Miel Vander Sande',
    url='https://github.com/viaacode/shacl2puml',
    author_email='miel.vandersande@meemoo.be',
    install_requires=requirements,
    keywords=['Linked Data', 'Semantic Web', 'Python',
              'SHACL', 'Shapes', 'Schema', 'Validate'],
    license='MIT',
    classifiers=[
                'Development Status :: 1 - Experimental',
                'Programming Language :: Python :: 3',

    ],
    entry_points = {
        'console_scripts': [
            'shacl2puml = shacl2puml.__main__:main'
        ]
    })