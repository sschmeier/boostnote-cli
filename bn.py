#!/usr/bin/env python
"""
NAME: bn.py
===========

DESCRIPTION
===========

INSTALLATION
============

USAGE
=====

VERSION HISTORY
===============

0.0.7    20191118    Double quotes now allowed for single line notes.
0.0.6    20191112    Changed default location on Dropbox.
0.0.5    20191002
0.0.4
0.0.3
0.0.2
0.0.1    2019XXXX    Initial version.

LICENCE
=======

See LICENSE file distributed with the repository.
2019, copyright Sebastian Schmeier
s.schmeier@protonmail.com // https://www.sschmeier.com

template version: 2.0 (2018/12/19)
"""
__version__ = "0.0.7"
__date__ = "20191118"
__email__ = "s.schmeier@protonmail.com"
__author__ = "Sebastian Schmeier"

import sys
import argparse
import csv
import gzip
import bz2
import zipfile
import time
import re
import datetime
import dateutil.parser
import collections
from pathlib import Path


# non-standard lib: For color handling on the shell
try:
    from colorama import init, Fore

    # INIT color
    # Initialise colours for multi-platform support.
    init()
    reset = Fore.RESET
    colors = {
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": "",
    }
except ImportError:
    sys.stderr.write(
        "colorama lib desirable. " + 'Install with "conda install colorama".\n\n'
    )
    reset = ""
    colors = {"success": "", "error": "", "warning": "", "info": ""}


def alert(atype, text, log, repeat=False, flush=False):
    if repeat:
        textout = "{} [{}] {}\r".format(
            time.strftime("%Y%m%d-%H:%M:%S"), atype.rjust(7), text
        )
    else:
        textout = "{} [{}] {}\n".format(
            time.strftime("%Y%m%d-%H:%M:%S"), atype.rjust(7), text
        )

    log.write("{}{}{}".format(colors[atype], textout, reset))
    if flush:
        log.flush()
    if atype == "error":
        sys.exit(1)


def success(text, log=sys.stderr, flush=True):
    alert("success", text, log, flush=flush)


def error(text, log=sys.stderr, flush=True):
    alert("error", text, log, flush=flush)


def warning(text, log=sys.stderr, flush=True):
    alert("warning", text, log, flush=flush)


def info(text, log=sys.stderr, repeat=False, flush=True):
    alert("info", text, log, repeat=repeat, flush=flush)


def parse_cmdline():
    """ Parse command-line args. """
    # parse cmd-line ----------------------------------------------------------
    description = "Simple command-line interface to Boostnote."
    version = "version {}, date {}".format(__version__, __date__)
    epilog = "Copyright {} ({})".format(__author__, __email__)

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument("--version", action="version", version="{}".format(version))

    parser.add_argument(
        "-d",
        "--dir",
        metavar="PATH",
        dest="dir",
        default="~/Dropbox/Apps/Boostnote/notes",
        help='Boostnote notes dir. Only used if no .bn config file present in home-dir. [default: "~/Dropbox/Apps/Boostnote/notes"]',
    )

    # sub programs
    subparsers = parser.add_subparsers(dest="subparser")

    parser_h = subparsers.add_parser("help", description="help.", help="Show help")

    # -----------------------------------------------------
    parser_v = subparsers.add_parser("v", description="View notes.", help="View notes")

    parser_v.add_argument(
        "v_str_search", metavar="STRING", help="String/RegExp to match in title"
    )

    # -----------------------------------------------------
    parser_s = subparsers.add_parser(
        "s", description="Search for notes.", help="Search for notes"
    )

    parser_s.add_argument(
        "s_str_search", metavar="STRING", help="String/RegExp to search in title/text"
    )

    parser_s.add_argument(
        "-f",
        "--fulltext",
        action="store_true",
        dest="s_fulltext",
        default=False,
        help="Search in fulltext instead",
    )

    parser_s.add_argument(
        "-p",
        "--print",
        action="store_true",
        dest="s_print",
        default=False,
        help="Print match in fulltext search",
    )

    ## future: search tags instead of title or fulltext
    parser_s.add_argument(
        "-t",
        "--tags",
        action="store_true",
        dest="s_tags",
        default=False,
        help="Search in tags instead",
    )

    # -----------------------------------------------------
    parser_ls = subparsers.add_parser(
        "ls", description="List notes.", help="List notes"
    )

    parser_ls.add_argument(
        "-c",
        "--created",
        action="store_true",
        dest="ls_created",
        default=False,
        help="List according to time created instead of updated",
    )

    parser_ls.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="ls_all",
        default=False,
        help="List all notes instead of last 10",
    )

    # -----------------------------------------------------
    parser_lst = subparsers.add_parser(
        "lst", description="List tags.", help="List tags"
    )

    parser_lst.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="lst_all",
        default=False,
        help="List all tags instead of 10 most frequent",
    )

    parser_lst.add_argument(
        "-s",
        "--sort",
        action="store_true",
        dest="lst_name",
        default=False,
        help="List tags alphabetically, prints all tags",
    )

    parser_lst.add_argument(
        "-n",
        "--notes",
        action="store_true",
        dest="lst_notes",
        default=False,
        help="List also notes belonging to the tags",
    )

    # if no arguments supplied print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    if args.subparser == "help":
        parser.print_help()
        sys.exit(1)

    return args, parser


def load_file(filename):
    """ LOADING FILES """
    if filename in ["-", "stdin"]:
        filehandle = sys.stdin
    elif filename.split(".")[-1] == "gz":
        filehandle = gzip.open(filename, "rt")
    elif filename.split(".")[-1] == "bz2":
        filehandle = bz2.open(filename, "rt")
    elif filename.split(".")[-1] == "zip":
        filehandle = zipfile.ZipFile(filename)
    else:
        filehandle = open(filename)
    return filehandle


class BNote:
    """ """

    def __init__(self, fileobj):
        self.file = fileobj
        self.tcreated = None
        self.ucreated = None
        self.tags = None
        self.title = None
        self.content = None
        self.parse()

    def parse(self):
        filehandle = open(self.file)
        data = filehandle.read()
        res = re.search('createdAt: "(.+?)"', data)
        assert res
        self.tcreated = dateutil.parser.parse(res.group(1))
        res = re.search('updatedAt: "(.+?)"', data)
        assert res
        self.tupdated = dateutil.parser.parse(res.group(1))
        res = re.search('title: "(.+?)"', data)
        assert res
        self.title = res.group(1)
        res = re.search("tags:\s+(\[.*?\])", data, re.S)
        assert res
        tags = res.group(1)
        tags = tags.replace('"\n', '",')
        self.tags = eval(tags)
        res = re.search("content:\s+(?:'''|\")(.+?)(?:'''|\")", data, re.S)
        assert res
        self.content = res.group(1)


def main():
    """ The main function. """
    args, parser = parse_cmdline()

    dirs = []
    # check for a config file with path information
    config = Path("~/.bn").expanduser().resolve()
    if config.exists():
        import yaml
        config = yaml.load(open(config).read(), Loader=yaml.SafeLoader)
        for d in config["dir"]:
            ndir = Path(d)
            ndir = ndir.expanduser().resolve()
            if ndir.exists():
                dirs.append(ndir)

        if len(dirs) == 0:
            error('None of the paths in the config file exist. EXIT.')
    else:
        # get notes path
        ndir = Path(args.dir)
        ndir = ndir.expanduser().resolve()
        dirs.append(ndir)
        if not ndir.exists():
            error('Path "{}" to notes does not exist. EXIT.'.format(ndir))

    notes = []
    for d in dirs:
        # scan for notes
        notes += ndir.glob("*.cson")

    if len(notes) == 0:
        error('No notes found in the path(s) specified. EXIT.')

    if args.subparser == "s":
        regex_query = re.compile(args.s_str_search, re.IGNORECASE)
    elif args.subparser == "v":
        regex_query = re.compile(args.v_str_search, re.IGNORECASE)

    # loop notes
    titles = []
    d_tags = {}
    for note in notes:
        note = BNote(note)

        # search notes
        if args.subparser == "s":
            res = 0
            if args.s_fulltext:
                res = regex_query.findall(note.content)
            elif args.s_tags:
                for tag in note.tags:
                    results = regex_query.match(tag)
                    if results:
                        res = 1
                        break
            else:
                res = regex_query.match(note.title)

            # print titles of matching notes
            if not res:
                continue
            else:
                if args.s_print and args.s_fulltext:
                    sys.stdout.write(
                        "{}\n{}\t{}\n{}\n{}\n".format(
                            "-" * 60,
                            note.title,
                            note.tupdated,
                            "-" * 60,
                            "\n".join(res),
                        )
                    )
                else:
                    sys.stdout.write("{}\t{}\n".format(note.title, note.tupdated))

        # view notes
        if args.subparser == "v":
            res = regex_query.match(note.title)
            # print matching notes
            if not res:
                continue
            else:
                sys.stdout.write(
                    "{}\n{}\t{}\n{}\n{}\n".format(
                        "-" * 60, note.title, note.tupdated, "-" * 60, note.content
                    )
                )
        # when listing notes, record time
        elif args.subparser == "ls":
            if args.ls_created:
                titles.append((note.tcreated, note.title))
            else:
                titles.append((note.tupdated, note.title))
        # listing tags
        elif args.subparser == "lst":
            for tag in note.tags:
                d_tags[tag] = d_tags.get(tag, []) + [note.title]

    if args.subparser == "ls":
        titles.sort()
        titles.reverse()
        if not args.ls_all:
            titles = titles[:10]
        for t in titles:
            sys.stdout.write("{}\t{}\n".format(t[1], t[0]))

    if args.subparser == "lst":
        if args.lst_name:
            sorted_d_tags = sorted(d_tags.items(), key=lambda kv: kv[0])
        else:
            sorted_d_tags = sorted(d_tags.items(), key=lambda kv: len(kv[1]))
            sorted_d_tags.reverse()  # large to small
            if not args.lst_all:
                sorted_d_tags = sorted_d_tags[:10]

        for t in sorted_d_tags:
            if args.lst_notes:
                a = t[1]
                a.sort()
                sys.stdout.write("{}\t{}\t{}\n".format(t[0], len(t[1]), "; ".join(a)))
            else:
                sys.stdout.write("{}\t{}\n".format(t[0], len(t[1])))

    return


if __name__ == "__main__":
    sys.exit(main())
