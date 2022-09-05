from setuptools import setup, find_packages

setup(
    name="pydeskui",
    version="0.0.1",
    author="openHacking",
    author_email="openHacking@126.com",
    description="Python TKinter Simple UI Components",
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/openHacking/TKinter-UI",
    python_requires=">=3.7",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={'pydeskui': ['assets/**/*']}
)