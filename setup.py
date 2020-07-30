import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wearables", # Replace with your own username
    version="0.0.1",
    author="Megan McMahon",
    author_email="mcmahonmc@utexas.edu",
    description="A package to conduct analysis of rest-activity data derived from wearable devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UTCogNeuroLab/wearables",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
