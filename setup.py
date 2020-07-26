import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

about = {}
path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "governor/__about__.py"
)
with open(path, "r", encoding='utf-8') as f:
    exec(f.read(), about)

setuptools.setup(
    name=about["name"],
    version=about["version"],
    author=about["author"],
    author_email=about["author_email"],
    description=about["description"],
    url=about["url"],
    long_description=long_description,
    long_description_content_type="text/markdown",
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
