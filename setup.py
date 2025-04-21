from setuptools import setup, find_packages
import os

# Read README.md if it exists, otherwise use a default description
long_description = "A protein binder design pipeline using LLM planning and structure prediction"
if os.path.exists("README.md"):
    with open("README.md") as f:
        long_description = f.read()

setup(
    name="plugpep",
    version="0.1.0",
    packages=find_packages(),
    author="Foad Nazari",
    author_email="foadnazari@gmail.com",
    description="A protein binder design pipeline using LLM planning and structure prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/foadnazari/plug-pep",
    install_requires=[
        "langchain>=0.1.5",
        "langchain-core>=0.1.5",
        "langchain-community>=0.0.10",
        "langchain-google-genai>=0.0.5",
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0"
    ]
)

