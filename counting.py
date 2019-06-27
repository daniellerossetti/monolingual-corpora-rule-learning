# this is a mix of biltrans-extract-frac-freq.py and biltrans-count-patterns-ngrams.py

import sys
import math

def get_ambiguous_set(lines):
  ambiguous_set = set()
  for i in range(1, len(lines)):
    # get words in line without ranking number, probability, and line number
    line1 = set(lines[i-1].split('\t')[3].split())
    line2 = set(lines[i].split('\t')[3].split())

    # get words that are different in each of the two lines
    ambiguous_set.update(line1.symmetric_difference(line2))

  return ambiguous_set

def get_frequency(lines, ambig):
  freq = {}
  for line in lines:
    for word in ambig:
      if word in line:
        probability = float(line.split('\t')[1])
        if word not in freq:
          freq[word] = probability
        else:
          freq[word] += probability
  
  return freq

def main():
  ranked = open(sys.argv[1], 'r')

  reading = True
  while reading:
    ranked_lines = []

    # there's an empty line between each group of lines in ranked
    line = ranked.readline() # for now while the first line is empty
    line = ranked.readline()
    while line != '\n':
      ranked_lines.append(line)
      line = ranked.readline()
    
    ambiguous_words = get_ambiguous_set(ranked_lines)
    print(ambiguous_words)
    reading = False
    
    frequency = get_frequency(ranked_lines, ambiguous_words)
    for word, freq in frequency.items():
      print(word + '\t' + str(freq))
      

if __name__ == "__main__":
  main()
