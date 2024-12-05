from setuptools import setup, find_packages

setup(
    name="recommendation_system",
    version="0.1.0",
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    install_requires=[
        "pandas",
        "numpy",
        "jupyter",
        "openfoodfacts",
        "notebook"
    ],
    python_requires=">=3.8",
    description="recommendation system for food products",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)