from setuptools import setup, find_packages

setup(
    name="chartengineer",  # Name of your package
    version="0.1.0",  # Initial version
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "dotenv",
        "plotly",
        "matplotlib",
        "colorcet",
        "nbformat>=4.2.0",
        "kaleido"
    ],
    author="Brandyn Hamilton",
    author_email="brandynham1120@gmail.com",
    description="Library for quick and modern chart building.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=" ",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or whatever license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
