import setuptools
import os

def load_requirements(fname="requirements.txt"):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, fname), encoding="utf-8") as f:
        # убираем пустые строки и комментарии
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytils-functions",
    version="0.2.4",
    author="Whispered",
    author_email="bluden99@example.com",
    description="Utils for data python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Whisperes/pytils",
    packages=setuptools.find_packages(exclude=("tests.*","docs.*")),
    install_requires=load_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)