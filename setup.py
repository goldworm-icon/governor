import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="governor",
    version="0.0.2",
    author="goldworm",
    author_email="goldworm@iconloop.com",
    description="Governor SCORE handler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goldworm-icon/governor",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': [
            'governor=governor.__main__:main'
        ]
    }
)
