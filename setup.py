#!/usr/bin/env python3
"""
Setup script for A700cli - Agent700 CLI Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    return [
        "requests>=2.32.0",
        "python-socketio>=5.11.0", 
        "python-dotenv>=1.1.0",
        "rich>=13.0.0"
    ]

setup(
    name="a700cli",
    version="1.3.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Enhanced Agent700 CLI with Interactive Configuration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/LinkAnalysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "a700cli=a700cli.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.ini"],
    },
    keywords="agent700, cli, ai, mcp, automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/LinkAnalysis/issues",
        "Source": "https://github.com/yourusername/LinkAnalysis",
        "Documentation": "https://github.com/yourusername/LinkAnalysis#readme",
    },
)