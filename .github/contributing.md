# PyTxUI Contributing Guide

## Technology stack

- Python 3.10.2
- Tkinter 8.6

## Development

### create virtual environment

```sh
# create new virtual environment , named .env_tkui
python -m venv .env_tkui
```

### activate virtual environment

For windows CMD

```sh
.\.env_tkui\Scripts\activate.bat
```

For Mac bash

```sh
source .env_tkui/bin/activate
```

other platform check: [venv](https://docs.python.org/3/library/venv.html)

For VS Code

1. `Ctrl+Shift+P`
2. Search `python interpreter`,choose `Python: Select Interpreter`
3. choose `.env_tkui` environment
4. Open a new `Command Prompt`(Windows) or new `bash`(Mac) in VS Code terminal

### install dependencies

```sh
# install dependencies from requirements.txt
pip install -r requirements.txt

# install pytxui by setup.py, delelop mode
python setup.py develop

```

### develop feature

```sh
cd pytxui
python demo.py
```

## Useful command

### add a denpendency

```sh
 # install xxx-module
pip install xxx-module

 # generate requirements.txt
pip freeze > requirements.txt
```

### remove a denpendency

```sh
 # uninstall xxx-module
pip uninstall xxx-module -y

 # generate requirements.txt
pip freeze > requirements.txt
```

### setup.py

```sh
python setup.py build
python setup.py install
# clear setup
python setup.py clean --all
```
