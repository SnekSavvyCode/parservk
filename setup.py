import importlib

from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_description = file.read()



metadata = importlib.import_module("parservk.version").__metadata__

setup(
	name=metadata["name"],
	version=metadata["version"],
	author=metadata["author"],
	author_email=metadata["author_email"],
	description=metadata["description"],
	long_description=long_description,
	url=metadata["url"],
	packages=find_packages(),
	install_requires=[],
	license=metadata["license"],
	keywords=metadata["keywords"],
	classifiers=metadata["classifiers"],
	python_requires=metadata["python_requires"]
)