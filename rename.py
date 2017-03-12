#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert file and directory names based on a set of criteria.  Can change case and replace a character or characters
with another group of characters.  Useful to convert all directory and file names to the same case.
However, this is recommended for use on data directories only.  Do not use on anything critical.
"""

import logging
import os
import os.path
import re
import string

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# -------------------------------- Constants ----------------------------------
LOWER = 1
UPPER = 2
CAPWORDS = 3

# Illegal path characters
INVALID_NT_CHARACTERS = r'"*/:<>?\|'
INVALID_POSIX_CHARACTERS = "/"

# Extra characters to remove
UNSAFE_PUNCTUATION = r'!"#$%&\'()*+,/:;<=>?@[\]^`{|}~'
SAFE_PUNCTUATION = ".-_"
PUNCTUATION = string.punctuation

# -------------------------------- Functions ----------------------------------
def contents(start_dir, show_files=False):
    """Lists directory and all subdirectories contents."""
    start_dir = start_dir.rstrip(os.sep)
    print('Directory listing for', start_dir)
    for root, dirs, files in os.walk(start_dir):
        print(root, 'contains...')
        print('Directories:',)
        if len(dirs) == 0:
            print('None')
        else:
            print(str(dirs).strip('[]'))
        if show_files:
            print('Files:',)
            if len(files) == 0:
                print('None')
            else:
                print(str(files).strip('[]'))

def convertCase(str_obj, case):
    """Convert file or directory case to that which is specifed."""
    if case == LOWER:
        str_obj = str_obj.lower()
    elif case == UPPER:
        str_obj = str_obj.upper()
    elif case == CAPWORDS:
        str_obj = string.capwords(str_obj)
    return str_obj

def rmPattern(str_obj, pattern, verbosity=0):
    """Removes specified pattern from a string."""
    if re.search(pattern, str_obj):
        if verbosity > 1: print("Removing pattern \"" + pattern + "\" from " + str_obj)
        str_obj = re.sub(pattern, "", str_obj)
    return str_obj

def rmPunctuation(str_obj, ignore=SAFE_PUNCTUATION):
    """Removes excess punctuation from directory or file name."""
    for c in PUNCTUATION:
        if c in ignore:
            continue
        else:
            str_obj = str_obj.replace(c, "")
    return str_obj

def rename(fs_obj, case=False, separators=None, pattern=None, rmpunc=False, ignore="", verbosity=0):
    """Converts file and directory names based on specific paramaters."""
    root = os.path.dirname(fs_obj)
    new_fs_obj = os.path.basename(fs_obj)
    if pattern:
        for pat in pattern:
            new_fs_obj = rmPattern(new_fs_obj, pat, verbosity)
    if rmpunc:
        if separators and separators[0] not in ignore:
            ignore = ignore + separators[0]
        if verbosity > 1: print("Removing punctuation... ",)
        if os.path.isfile(fs_obj) and "." not in ignore:
            ignore = ignore + "."
        new_fs_obj = rmPunctuation(new_fs_obj, ignore)
        if verbosity > 1: print(root + os.sep + new_fs_obj)
    new_fs_obj = new_fs_obj.strip()
    if separators:
        new_fs_obj = separator(new_fs_obj, separators)
    if case:
        new_fs_obj = convertCase(new_fs_obj, case)
    if root:
        new_fs_obj = root + os.sep + new_fs_obj
    if new_fs_obj == fs_obj:
        if verbosity > 0: print('No changes were made to', fs_obj)
    else:
        if verbosity > 0: print('Converting', fs_obj, 'to', new_fs_obj)
        os.rename(fs_obj, new_fs_obj)

def separator(str_obj, separators):
    """Convert word separators from one string to another in a directory or file name."""
    if os.name == 'nt':
        for sep in separators:
            for c in sep:
                if c in INVALID_NT_CHARACTERS:
                    raise OSError("Character not allowed in file or directory names for your operating system.")
    else:
        for sep in separators:
            for c in sep:
                if c in INVALID_POSIX_CHARACTERS:
                    raise OSError("Character not allowed in file or directory names for your operating system.")
    str_obj = str_obj.replace(separators[0], separators[1])
    return str_obj

# -----------------------------------------------------------------------------
#                                Main Function
# -----------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser()
    case_grp = parser.add_mutually_exclusive_group()
    case_grp.add_argument("-c", "--capwords", action="store_const", const=3, dest="case",
                          help="Converts case of file and/or directories to capwords. Mutually exclusive with -l and -u.")
    parser.add_argument("-f", "--files", action="store_true", dest="files",
                        help="Modify the names of all files not just directories.")
    parser.add_argument("-i", "--ignore", action="store", nargs=1, dest="ignore", default="",
                        help="List of punctuation characters that will not be removed under any circumstance.")
    case_grp.add_argument("-l", "--lower", action="store_const", const=1, dest="case",
                          help="Converts case of file and/or directories to lowercase. Mutually exclusive with -l and -u.")
    parser.add_argument("-L", "--list", action="store_true", dest="list_only",
                        help="List all directories (and optionally files) in the directory to be scanned.")
    parser.add_argument("-p", "--remove-punctuation", action="store_const", const=1, dest="rmpunc",
                        help="Removes most punctuation from directory and file names except \".\", \"-\", and \"_\".")
    parser.add_argument("-q", "--quiet", action="store_const", const=0, dest="verbosity",
                        help="Turns off all output")
    parser.add_argument("-r", "--regex", action="store", nargs=1, dest="pattern", default="",
                        help="Comma separated list of regex to remove.")
    parser.add_argument("-s", "--separators", action="store", nargs=2, dest="separators", default=(),
                        help="Character to separate words in a directory or file name.  Choices: space, underscore [default]")
    case_grp.add_argument("-u", "--upper", action="store_const", const=2, dest="case",
                          help="Converts case of file and/or directories to uppercase. Mutually exclusive with -l and -u.")
    parser.add_argument("-v", "--verbose", action="count", dest="verbosity", default=1,
                        help="Prints varying degrees of verbosity to stdout.")
    parser.add_argument("--convert-start-dir", action="store_true", dest="convert_start",
                        help="Convert starting directory as well.")
    parser.add_argument("--remove-all-punctuation", action="store_const", const=2, dest="rmpunc",
                        help="Removes all punctuaion from directories.  Leaves periods in file names.")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("Incorrect number of arguments.")
    else:
        start_dir = args[0]
        verbosity = options.verbosity
        case = options.case
        ws = options.separators
        pat = options.pattern
        if pat:
            pat = pat.split()
        rmpunc = options.rmpunc
        ignore = options.ignore
    if options.list_only:
        contents(start_dir, options.files)
    else:
        if verbosity > 0: print('Beginning conversion...')
        start_dir = start_dir.rstrip(os.sep)
        if verbosity > 0: print('Starting directory is:', start_dir)
        for root, dirs, files in os.walk(start_dir, topdown=False):
            if verbosity > 1: print('Directory', root + '...',)
            if len(dirs) > 0 or (options.files and len(files) > 0):
                if verbosity > 1: print()
                for directory in dirs:
                    olddir = root + os.sep + directory
                    rename(olddir, case, ws, pat, rmpunc, ignore, verbosity)
                if options.files and len(files) > 0:
                    for cfile in files:
                        oldfile = root + os.sep + cfile
                        rename(oldfile, case, ws, pat, rmpunc, ignore, verbosity)
            else:
                if verbosity > 1: print('Empty')
        if options.convert_start:
            if verbosity > 0: print('Converting start directory')
            rename(start_dir, case, ws, pat, rmpunc, ignore, verbosity)

# ---------- Call main function if file is run as top level script ----------
if __name__ == "__main__": main()
