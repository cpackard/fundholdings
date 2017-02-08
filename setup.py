from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    licence = f.read()

setup(
    name='holdings',
    version='0.1',
    description='Scrape and parse mutual fund holdings from EDGAR.',
    long_description=readme,
    author='Christian N Packard',
    author_email='chrisnpack@gmail.com',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'requests',
        'bs4',
    ]
)

