# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
#
# UTIL
#
# Support libraries. File and dict handling.
# 

import os


def shortname(filepath):
    """
    Return short name for input file (basename minus extension)
    filepath -- full path to input file
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
