from setuptools import setup


setup(
    name='BoPlatsAutomatic',
    version='1',
    description='automation of boplats searching',
    author='Nick.Well',
    author_email='nick2018w@gmail.com',
    packages=['boplats'],
    install_requires=[
        'selenium',
        'beautifulsoup4',
        'webdriver_manager',
        'pynput'
    ],
)