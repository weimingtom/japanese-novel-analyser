"""
config.py: This file stores default configuration options.
"""

import sys
import os.path

# string to use for accumulating functionality
IGNORE = '#'
  
formatter = 'aozora'
encoding  = 'utf-8'
output    = None
dbfile    = 'data/freqs.db'
gaijifile ='data/gaiji_codes'
mecab_fields = 6 # mecab pos fields, should not change
top_number = 30

def get_basedir():
  return os.path.normpath(os.path.join(
      os.path.split(sys.argv[0])[0], os.pardir))
