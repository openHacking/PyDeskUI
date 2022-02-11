import setuptools

setuptools.setup(
    name="pytxui",
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
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
     include_package_data=True,
    package_data={'pytxui': ['assets/**/*']}
)