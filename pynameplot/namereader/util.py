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

def get_axisticks(bounds):
    """
    Given a boundary tuple, will calculate a reasonable set of axis tick marks
    :param bounds: tuple
    :return: list
    """
    if bounds[1] - bounds[0] > 20:
        sep = 20
    elif bounds[1] - bounds[0] > 10:
        sep = 10
    else:
        sep = 2

    start = bounds[0]
    while start%sep != 0:
        start += 1

    return [float(i) for i in range(start, bounds[1], sep)]