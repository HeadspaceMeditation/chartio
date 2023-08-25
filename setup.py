from setuptools import setup

setup(
    name='GingerioChartioUtilities',
    version='0.1',
    author='Jeremy A Johnson',
    author_email='jeremy@ginger.io',
    packages=['chartio'],
    scripts=[],
    url='https://github.com/HeadspaceMeditation/chartio',
    license='LICENSE',
    description='Chart.io Utilities',
    long_description=open('README.md').read(),
    install_requires=[
        "Pillow>=2.3.0",
        "PyPDF2>=1.19",
        "selenium>=2.31.0",
    ],
)
