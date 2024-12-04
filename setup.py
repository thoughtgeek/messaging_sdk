from setuptools import setup, find_packages

setup(
    name="messaging_sdk",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
    ],
)
