"""
formats.py: This file contains formatter for converting specially
formatted files into plain texts.
"""

from logger import logger

"""
This formatter takes texts in plain format and returns exactly the
same text.
"""
class PlainFormat:
  def trim(self, string):
    return string

"""
This formatter takes texts in the Aozora Bunko format and
strips and/or converts special Aozora constructs to gain plain text.
Gaiji constructs are replaced with UTF-8 equivalents and
other formatting constructs are deleted.
"""
class AozoraFormat:
  def __init__(self):
    #TODO: read Gaiji file
    pass

  def trim(self, string):
    #TODO: actual trimming
    return string
