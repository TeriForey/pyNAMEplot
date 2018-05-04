#!/usr/bin/env python

# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
#
# HEADER
# 
# Support libraries. Read header from NAME geochemical data file
# into named data structure.
#

def loadheader(filename):
    """
    Load NAME file and parse header lines into dict.
    filename -- input NAME file
    """
    header = {}
    
    with open(filename, 'r') as f:
        
        for line in range(1, 19):
            h = f.readline()
            
            if ":" in h:
                (key, val) = h.split(":", 1)
                key = key.strip()
                val = val.strip()
            
                header[key] = val

    return header
