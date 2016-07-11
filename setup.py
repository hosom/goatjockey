#!/usr/bin/python

from distutils.core import setup

setup(name='goatjockey',
	version='0.1',
	description='Python module for filtering threat intel feeds',
	author='Stephen Hosom',
	author_email='0xhosom@gmail.com',
	url='https://github.com/hosom/goatjockey',
	packages=['goatjockey'],
	install_requires=[
		'requests',
	],
	)
