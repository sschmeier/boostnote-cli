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

### Specify where to find your notes

The default path for the tool to look for notes is in `~/Dropbox/Apps/Boostnote/notes`. 
If you wish to change this path or add other paths where the tools should look, you need to use the `.bn` config-file.
Copy the `.bn` config-file to your home directory.
In this file you can specify a list of paths, where the tools will look for note-files.
In case the default path (`~/Dropbox/Apps/Boostnote/notes`) is sufficient for your use case, there is no need to use the `.bn` config-file.


## Usage

Five subcommands are currently available:

- help
- list (ls)
- listtags (lst)
- view (v)
- search (s)

### `bn help`

```bash
$ bn help
usage: bn [-h] [--version] [-d PATH] {help,v,s,ls,lst} ...

Simple command-line interface to Boostnote.

positional arguments:
  {help,v,s,ls,lst}
    help               Show help
    v                  View notes
    s                  Search for notes
    ls                 List notes
    lst                List tags

optional arguments:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  -d PATH, --dir PATH  Boostnote notes dir. [default:
                       "~/Dropbox/Apps/Boostnote/notes"]
```


### `bn ls`

`bn ls` will list by default the last ten updated notes.
You can change the behavior by using arguments to the `bn ls` command:

- `-c`: List according to creation date
- `-a`: List all notes not only last ten


### `bn lst`

`bn lst` will list by default the ten most frequent tags from your notes.
You can change the behavior by using arguments to the `bn lst` command:

- `-a`: List all notes not only ten most frequent ones
- `-s`: List alphabetically, which will also print all tags
- `-n`: List notes belonging to the tags


### `bn v`

`bn v` can be used to look at notes matching a string or match a regular expression in the title.
If more then one note matches the string/regexp, all will be printed.


### `bn s`

`bn s` is used to search for notes that contain a string or match a regular expression in the title, content, or tags.
You can change the behavior by using arguments to the `bn lst` command:

- `-f`, `--fulltext`: Search in fulltext instead
- `-p`, `--print`: Print match in fulltext search
- `-t`, `--tags`: Search in tags instead


Specifically the use of regular expressions in combination with `-pf` can facilitate a quick look at the lines a match occurred in per note, for example:

```bash
# Print all notes and complete lines where the word data was found:
$ bn s -pf ".*data.*"
```
