#!/usr/bin/env python3
"""
Ca' Foscari Ultimate Study System - Setup Script
Emre Aras (907842) - Computer Architecture
"""

from setuptools import setup, find_packages

setup(
    name="cafoscari-ultimate-system",
    version="1.0.0",
    author="Emre Aras",
    author_email="907842@stud.unive.it",
    description="AI-Powered Study Management System for Ca' Foscari University",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/emrearas/CaFoscariUltimate",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "anthropic>=0.25.0",
        "schedule>=1.2.0",
        "google-auth>=2.23.0",
        "google-auth-oauthlib>=1.1.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.100.0",
        "PyPDF2>=3.0.1",
        "pdfplumber>=0.9.0",
        "pytesseract>=0.3.10",
        "Pillow>=10.0.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "video": ["opencv-python>=4.8.0", "moviepy>=1.0.3"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "cafoscari-system=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)