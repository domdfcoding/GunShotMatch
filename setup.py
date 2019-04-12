from setuptools import setup, find_packages

setup(
	name="GunShotMatch",
	version="1.0,0",
    author='Dominic Davis-Foster',
	author_email="dominic@davis-foster.co.uk",
	packages=find_packages(),
	license="GNU General Public License v3.0",
	url="http://github.com/domdfcoding/GunShotMatch/",
	description='A Python program to semi-automatically match organic compounds between GSR samples',
	install_requires=[
	        "sklearn",
			"numpy>=1.16.2",
			"pandas>=0.24.1",
			"openpyxl>=2.5.14",
			"matplotlib>=3.0.3",
			"scipy>=1.2.1",
			"PyMassSpec>=2.1.0",
        	],
)
