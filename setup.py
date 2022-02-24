from setuptools import setup
import os
import sys

from blockchain_exploration import VERSION

if sys.argv[-1] == 'publish':
    os.system("rm -r dist")
    os.system("python3 setup.py clean --all")
    os.system("python3 setup.py sdist")
    os.system("python3 setup.py bdist_wheel")
    os.system("python3 -m twine upload --config-file .pypirc -r veeanexus dist/*")
    curr_version = os.popen("ls dist/|grep tar").read()
    print("published " + curr_version)
    sys.exit()

with open('README.md', 'r') as input:
    long_description = input.read()

setup(
    name='blockchain-exploration',
    version=VERSION,
    description='Exploring the blockchain with hyperlinks',
    long_description=long_description,
    keywords='blockchain link hyperlink sweet',
    license='Proprietary (© Sweet)',
    author="Owen Miller",
    include_package_data=True,
    author_email='Owen Miller <owen@sweet.io>',
    python_requires='>=3.7',
    url='https://github.com/sweet-io-org/blockchain_exploration',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3 :: Only',
        "Operating System :: OS Independent",
    ],
    packages=['blockchain_exploration'],
    install_requires=[
        'twine'  # Publication of projects https://pypi.org/project/twine/
    ]
)
