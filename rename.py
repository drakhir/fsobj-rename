#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert file and directory names based on a set of criteria.  Can change case and replace a
character or characters with another group of characters.  Useful to convert all directory and
file names to the same case. However, this is recommended for use on data directories only.
Do not use on anything critical.
"""

import os
import os.path
import re
import string

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
        if not dirs:
            print('None')
        else:
            print(str(dirs).strip('[]'))
        if show_files:
            print('Files:',)
            if not files:
                print('None')
            else:
                print(str(files).strip('[]'))

def convert_case(str_obj, case):
    """Convert file or directory case to that which is specifed."""
    if case == LOWER:
        str_obj = str_obj.lower()
    elif case == UPPER:
        str_obj = str_obj.upper()
    elif case == CAPWORDS:
        str_obj = string.capwords(str_obj)
    return str_obj

def rm_pattern(str_obj, pattern):
    """Removes specified pattern from a string."""
    if re.search(pattern, str_obj):
        str_obj = re.sub(pattern, "", str_obj)
    return str_obj

def rm_punctuation(str_obj, ignore=SAFE_PUNCTUATION):
    """Removes excess punctuation from directory or file name."""
    for char in PUNCTUATION:
        if char in ignore:
            continue
        else:
            str_obj = str_obj.replace(char, "")
    return str_obj

# TODO: Refactor - catch errors, etc.
def rename(fs_obj, case=False, separators=None, pattern=None, rmpunc=False, ignore=""):
    """Converts file and directory names based on specific paramaters."""
    root = os.path.dirname(fs_obj)
    new_fs_obj = os.path.basename(fs_obj)
    if pattern:
        for pat in pattern:
            new_fs_obj = rm_pattern(new_fs_obj, pat)
    if rmpunc:
        if separators and separators[0] not in ignore:
            ignore = ignore + separators[0]
        if os.path.isfile(fs_obj) and "." not in ignore:
            ignore = ignore + "."
        new_fs_obj = rm_punctuation(new_fs_obj, ignore)
    new_fs_obj = new_fs_obj.strip()
    if separators:
        new_fs_obj = separator(new_fs_obj, separators)
    if case:
        new_fs_obj = convert_case(new_fs_obj, case)
    if root:
        new_fs_obj = root + os.sep + new_fs_obj
    if new_fs_obj == fs_obj:
        msg = "No changes were made to %s" % fs_obj
    else:
        msg = "Converting %s to %s" % (fs_obj, new_fs_obj)
        os.rename(fs_obj, new_fs_obj)
    return msg

def separator(str_obj, separators):
    """Convert word separators from one string to another in a directory or file name."""
    for sep in separators:
        for char in sep:
            if os.name == 'nt':
                if char in INVALID_NT_CHARACTERS:
                    raise OSError("Character %s not allowed in %s filesystem objects."
                                  % (char, os.name))
            else:
                if char in INVALID_POSIX_CHARACTERS:
                    raise OSError("Character %s not allowed in %s filesystem objects."
                                  % (char, os.name))
    str_obj = str_obj.replace(separators[0], separators[1])
    return str_obj

def parse_args():
    """Set/Parse arguments"""
    desc = "Rename files and directories based on a specific criteria."
    import argparse
    parser = argparse.ArgumentParser(description=desc)
    case_grp = parser.add_mutually_exclusive_group()
    case_grp.add_argument("-c", "--capwords", action="store_const", const=3, dest="case",
                          help="Converts case of file and/or directories to capwords. \
                          Mutually exclusive with -l and -u.")
    parser.add_argument("-f", "--files", action="store_true", dest="files",
                        help="Modify the names of all files not just directories.")
    parser.add_argument("-i", "--ignore", action="store", nargs=1, dest="ignore", default="",
                        help="List of punctuation that will not be removed under any circumstance.")
    case_grp.add_argument("-l", "--lower", action="store_const", const=1, dest="case",
                          help="Converts case of file and/or directories to lowercase.")
    parser.add_argument("-L", "--list", action="store_true", dest="list_only",
                        help="List all directories (and optionally files) in directory \
                        to be scanned.")
    parser.add_argument("-p", "--remove-punctuation", action="store_const", const=1, dest="rmpunc",
                        help="Removes most punctuation from directory and file names except \
                        \".\", \"-\", and \"_\".")
    parser.add_argument("-q", "--quiet", action="store_const", const=0, dest="verbosity",
                        help="Turns off all output")
    parser.add_argument("-r", "--regex", action="store", nargs=1, dest="pattern", default="",
                        help="Comma separated list of regex to remove.")
    parser.add_argument("-s", "--separators", action="store", nargs=2, dest="separators",
                        default=(),
                        help="Character to separate words in a directory or file name. \
                        Choices: space, underscore [default]")
    case_grp.add_argument("-u", "--upper", action="store_const", const=2, dest="case",
                          help="Converts case of file and/or directories to uppercase.")
    parser.add_argument("--convert-start-dir", action="store_true", dest="convert_start",
                        help="Convert starting directory as well.")
    parser.add_argument("--remove-all-punctuation", action="store_const", const=2, dest="rmpunc",
                        help="Removes all punctuaion from directories. Leave \".\" in file names.")
    parser.add_argument("start_dir", action="store", help="Starting directory.")
    args = parser.parse_args()
    return args

# -----------------------------------------------------------------------------
#                                Main Function
# -----------------------------------------------------------------------------
def main():
    """Main function"""
    # Get args
    args = parse_args()

    start_dir = args.start_dir
    case = args.case
    wsep = args.separators
    pat = args.pattern
    if pat:
        pat = pat.split()
    rmpunc = args.rmpunc
    ignore = args.ignore
    if args.list_only:
        contents(start_dir, args.files)
    else:
        print('Beginning conversion...')
        start_dir = start_dir.rstrip(os.sep)
        print('Starting directory is:', start_dir)
        for root, dirs, files in os.walk(start_dir, topdown=False):
            print('Directory', root + '...',)
            if dirs or (args.files and files):
                print()
                for directory in dirs:
                    olddir = root + os.sep + directory
                    rename(olddir, case, wsep, pat, rmpunc, ignore)
                if args.files and files:
                    for cfile in files:
                        oldfile = root + os.sep + cfile
                        rename(oldfile, case, wsep, pat, rmpunc, ignore)
            else:
                print('Empty')
        if args.convert_start:
            print('Converting start directory')
            rename(start_dir, case, wsep, pat, rmpunc, ignore)

# ---------- Call main function if file is run as top level script ----------
if __name__ == "__main__":
    main()
