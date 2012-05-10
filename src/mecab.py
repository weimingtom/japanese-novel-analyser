# -*- coding: utf-8 -*-
"""
mecab.py: This file invokes the Mecab morphological analyser on the
cleaned input files and parses its output for further processing.
"""

import sys
import re
import MeCab

from logger import logger

class MecabData():
  def __init__(self, word, pos):
    self.word = word
    self.pos = pos

  def __repr__(self):
    return self.word + ' (' + ','.join(self.pos) + ')'

class PyMeCab():
  def __init__(self):
    self.tagger = MeCab.Tagger('')

  def parse(self, line):
    taglines = self.tagger.parse(line.encode('utf-8')).split('\n')
    data = []
    for tags in taglines:
      fields = re.split('[\t,]', tags)
      l = len(fields)
      if l > 7:
        word = fields[0]
        pos = fields[1:7]
        if fields[7] != '*': # take root instead of conjugation
          word = fields[7] 
        data.append(MecabData(word, pos))
      elif l > 1 and l < 7:
        logger.err('incomplete parse: %s' % tags)
      # else empty line
    return data

