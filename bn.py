#!/usr/bin/env python
"""
NAME: bn
=========

DESCRIPTION
===========

INSTALLATION
============

USAGE
=====

VERSION HISTORY
===============

0.0.1    2019    Initial version.

LICENCE
=======
2019, copyright Sebastian Schmeier
s.schmeier@protonmail.com // https://www.sschmeier.com

template version: 2.0 (2018/12/19)
"""
__version__ = "0.0.1"
__date__ = "20191001"
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
        default="~/Dropbox/Boostnote/notes",
        help='Boostnote notes dir. [default: "~/Dropbox/Boostnote/notes"]',
    )

    # sub programs
    subparsers = parser.add_subparsers(dest='subparser')

    parser_h = subparsers.add_parser('help', description="help.", help="Show help")
 
    parser_s = subparsers.add_parser('s', description="Search for notes.", help="Search for notes")
    parser_s.add_argument(
        "s_str_search",
        metavar="STRING",
        help='String to search in title/text',
    )
    
    parser_s.add_argument(
        "-f",
        "--fulltext",
        action="store_true",
        dest="s_fulltext",
        default=False,
        help='Search in full text. [default: "Search in title only"]',
    )

    parser_ls = subparsers.add_parser('ls', description="List notes.", help="List notes")

    parser_ls.add_argument(
        "-c",
        "--created",
        action="store_true",
        dest="ls_created",
        default=False,
        help='List according to time created. [default: "Time updated"]',
    )
    parser_ls.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="ls_all",
        default=False,
        help='List all notes. [default: "List last 10"]',
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


def main():
    """ The main function. """
    args, parser = parse_cmdline()

    # get notes path
    ndir = Path(args.dir)
    ndir = ndir.expanduser().resolve()
    if not ndir.exists():
        error('Path "{}" to notes does not exist. EXIT.'.format(ndir))
    
    # scan for notes
    notes = ndir.glob("*.cson")

    # regexps
    regex_title = re.compile('title:\s+"(.+)"')

    if args.subparser=="s":
        regex_query = re.compile(args.s_str_search, re.IGNORECASE)
    elif args.subparser == "ls":
        if args.ls_created:
            regex_time = re.compile('createdAt: "(.+)"')
        else:
            regex_time = re.compile('updatedAt: "(.+)"')

    # loop notes
    titles = []
    for note in notes:
        text = note.read_text()

        # get title
        res1 = regex_title.search(text)
        assert(res1)
        title = res1.group(1)

        # search notes
        if args.subparser=="s":
            if args.s_fulltext:
                text_tmp = text.replace("\n"," ")
                #print(text)
                #print(text_tmp)
                res = regex_query.match(text_tmp)
                print(res)
            else:
                res = regex_query.match(title)



            # print matching notes
            if not res:
                continue
            else:
                sys.stdout.write(text)
                sys.stdout.write("{}\n".format("-"*60))

        # when listing notes, record time
        elif args.subparser=="ls":
            res2 = regex_time.search(text)
            assert(res2)
            rtime = res2.group(1)
            dt = dateutil.parser.parse(rtime)
            titles.append((dt,title))


    if args.subparser=="ls":
        titles.sort()
        titles.reverse()
        if not args.ls_all:
            titles = titles[:10]
        for t in titles:
            #print(t)
            sys.stdout.write("{} | {}\n".format(t[1], t[0]))
    
    return


if __name__ == "__main__":
    sys.exit(main())
