# Boostnote CLI

Very simple CLI program to search and list [Boostnote](https://boostnote.io/) notes.

## Installation

###  Clone

```bash
git clone https://github.com/sschmeier/boostnote-cli.git 
```

### Change mode

```
cd boostnote-cli
chmod +x bn.py
```

### Make symbolic link

If you want to use bn.py everywhere you have two options.

1. Copy the bn.py to a directory on your `$PATH`, e.g. `~/bin`
2. Make a symbolic link in a directory on your `$PATH`, e.g. `~/bin` (PREFERRED)

```bash
# 1.
cp /PATH/TO/bn.py ~/bin

# 2.
cd ~/bin
ln -s /PATH/TO/bn.py bn
```

The second options has the advantage that you can update the bn.py easily without any new installs:

```
cd /PATH/TO/boostnote-cli
git pull
```


## Usage

- help
- list
- view
- search