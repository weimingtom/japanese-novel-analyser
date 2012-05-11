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
    node = self.tagger.parseToNode(line.encode('utf-8'))
    data = []
    while node:
      stat = node.stat
      if stat == 0 or stat == 1: # MECAB_NOR_NODE or MECAB_UNK_NODE
        word = node.surface
        fields = node.feature.split(',')
        pos = fields[0:6]
        if fields[6] != '*': # take root instead of conjugation
          word = fields[6] 
        data.append(MecabData(word, pos))
      # else MECAB_BOS_NODE or MECAB_EOS_NOD, egnoro
      node = node.next
    return data

