# PyTxUI Contributing Guide

## Technology stack

- Python 3.10.2
- Tkinter 8.6

## Development

### install dependencies

```shell
pip install -r requirements.txt # install dependencies from requirements.txt
```

or

```shell
python setup.py develop
```

### dev mode

```shell
cd pytxui
python demo.py
```

### add a denpendency

```shell
pip install xxx-module # install xxx-module
pip freeze > requirements.txt # generate requirements.txt
```

### install local

root path

```shell
python setup.py build
python setup.py install
```
