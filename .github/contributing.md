# PyTxUI Contributing Guide

## Technology stack

- Python 3.10.2
- Tkinter 8.6

## Development

### 1. Create virtual environment

```shell
# create new virtual environment , named .env_tkui
python -m venv .env_tkui
```

### 2. Activate virtual environment

For windows CMD

```shell
.\.env_tkui\Scripts\activate.bat
```

For Mac bash

```shell
source .env_tkui/bin/activate
```

other platform check: [venv](https://docs.python.org/3/library/venv.html)

For VS Code

1. `Ctrl+Shift+P`
2. Search `python interpreter`,choose `Python: Select Interpreter`
3. choose `.env_tkui` environment
4. Open a new `Command Prompt` in VS Code terminal


### 3. Install dependencies

```shell
# install dependencies from requirements.txt
pip install -r requirements.txt

# install pytxui by setup.py, delelop mode
python setup.py develop

```
### 4. Develop feature

```shell
cd src/pytxui && python demo.py
```

## Useful command

### add a denpendency

```shell
 # install xxx-module
pip install xxx-module

 # generate requirements.txt
pip freeze > requirements.txt
```

### remove a denpendency

```shell
 # uninstall xxx-module
pip uninstall xxx-module -y

 # generate requirements.txt
pip freeze > requirements.txt
```

### setup.py

```shell
python setup.py build
python setup.py install
# clear setup
python setup.py clean --all
```

### Build distribution
```shell
py -m pip install --upgrade build
py -m build
```

### Publish to PyPI

```shell
py -m pip install --upgrade twine
twine upload dist/*
```