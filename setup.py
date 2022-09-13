import setuptools


with open("README.md", "r") as readme:
    long_description = readme.read()


setuptools.setup(
    name="quarkapi",
    version="1.1",
    author="Anatoly Frolov (anafro)",
    author_email="contact@anafro.ru",
    description="The Quark API for Python developers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anafro/quark-api-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
