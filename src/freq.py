"""
freq.py: This file computes up the frequencies of the words given my
the morphological analyser by aggregating based on the root form and the
part-of-speech.
"""

class FrequencyCounter():
  def __init__(self):
    self.freqs = {}

  def add_word(self, word_data):
    word = word_data.word
    if word in self.freqs:
      self.freqs[word] = self.freqs[word] + 1
    else:
      self.freqs[word] =  1

  def display_list(self):
    pass
