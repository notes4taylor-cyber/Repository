#!/usr/bin/env python3
"""Setup script for PropertyFlow - Property Management Automation."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="propertyflow",
    version="1.0.0",
    author="PropertyFlow",
    author_email="support@propertyflow.com",
    description="Property Management Automation for NoVA Property Managers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/propertyflow/propertyflow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses standard library only!
    ],
    extras_require={
        "email": ["sendgrid>=6.9.0"],
        "sms": ["twilio>=8.0.0"],
        "database": ["sqlalchemy>=2.0.0"],
        "api": ["fastapi>=0.100.0", "uvicorn>=0.23.0"],
        "full": [
            "sendgrid>=6.9.0",
            "twilio>=8.0.0",
            "sqlalchemy>=2.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "propertyflow=property_management.cli:main",
        ],
    },
    include_package_data=True,
    keywords="property management, automation, real estate, landlord, tenant, rent collection",
)
