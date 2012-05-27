"""
config.py: This file stores default configuration options.
"""

import sys
import os.path

# string to use for displaying all entries
ALL = u'*'

# default format for input files
formatter = 'plain'
# encoding of input files
encoding  = 'utf-8'
# database file
dbfile    = 'data/freqs.db'
# default tablename
tablename = 'main'
# file containing unicode equivalents for gaiji codes
gaijifile ='data/jisx0213-2004-8bit-std.txt'
# number of mecab pos fields to use
mecab_fields = 5
# number of items to load to word list
list_number = 100

# get path of main program directory
def get_basedir():
  return os.path.normpath(os.path.join(
      os.path.split(sys.argv[0])[0], os.pardir))
