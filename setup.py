"""Setup script for geological interpretation agent."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="geo-agent",
    version="1.0.0",
    author="Geological AI Team",
    description="AI-powered geological interpretation and inversion system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "ollama>=0.1.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.15.0",
        "Pillow>=10.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "jinja2>=3.1.0",
        "markdown>=3.5.0",
        "click>=8.1.0",
        "rich>=13.6.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "geo-agent=cli.main:cli",
        ],
    },
)
