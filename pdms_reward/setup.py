"""
Setup script for PDMS Reward Function module
PDMS奖励函数模块安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="pdms_reward",
    version="1.0.0",
    author="RecogDrive Team",
    description="Complete PDMS (Planning Decision Making Scoring) computation for reward function usage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FengYun0611/recogdrive",
    packages=find_packages(exclude=["examples", "tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "shapely>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0",
            "flake8>=3.9.0",
        ],
        "viz": [
            "matplotlib>=3.3.0",
        ],
    },
    include_package_data=True,
    package_data={
        "pdms_reward": ["README.md", "requirements.txt"],
    },
)
