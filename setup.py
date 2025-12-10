"""Setup configuration for molbox_tester."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="molbox_tester",
    version="0.1.0",
    author="ravoegtlin",
    description="A telnet client for sending commands to Molbox via Moxa",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ravoegtlin/molbox_tester",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "telnetlib3>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "molbox=molbox_tester.main:main",
        ],
    },
)
