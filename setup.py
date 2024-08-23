from setuptools import setup, find_packages
setup(
	name="parservk",
	version="1.1",
	packages=find_packages(),
	install_requires=["requests==2.31.0", "grequests==0.7.0"],
	license="MIT"
)