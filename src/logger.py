"""
logger.py: This file defines a singleton logger for information
and error messages.
"""

from __future__ import print_function
import sys

class AnalyserLogger:
  def __init__(self, v=1):
    self.verbosity = v
    self.outstream = sys.stdout
    self.errstream = sys.stderr

  def __del__(self):
    self.outstream.flush()
    self.errstream.flush()
    self.outstream.close()
    self.errstream.close()

  def __write(self, string, v, stream):
    if(v <= self.verbosity):
      print(string, file=stream)

  def out(self, string, v=0):
    self.__write(string, v, self.outstream)

  def err(self, string, v=0):
    self.__write(string, v, self.errstream)

logger = AnalyserLogger()
