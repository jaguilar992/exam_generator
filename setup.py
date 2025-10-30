#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="exam-generator",
    version="1.0.1",
    author="Antonio Aguilar",
    author_email="jaguilar992@gmail.com",
    description="A Python library for generating professional multiple-choice exam PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaguilar992/exam_generator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "qrcode>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "exam_generator": ["assets/*", "fonts/*"],
    },
)