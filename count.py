# biltrans-extract-frac-freq.py + biltrans-count-patterns-ngrams.py + ngram-pruning-frac.py
import sys

def get_ambiguous(lines):
  ambiguous = set()
  for i in range(1, len(lines)):
    first = set(lines[i-1].split('\t')[2].split('$ ^'))
    second = set(lines[i].split('\t')[2].split('$ ^'))
    ambiguous.update(first.symmetric_difference(second))
  
  return ambiguous

def insert_ngrams(ngrams, freq, sl, tl, prob):
  if sl not in freq:
    freq[sl] = {}
  
  for ngram in ngrams:
    if ngram not in freq[sl]:
      freq[sl][ngram] = {}

  for ngram in ngrams:
    if tl not in freq[sl][ngram]:
      freq[sl][ngram][tl] = prob
    else:
      freq[sl][ngram][tl] += prob

def wrap(lst):
  return '^' + '$ ^'.join(lst) + '$'

def get_ngrams(words, i, max_ngrams, ngrams):
   if max_ngrams == 2:
     ngrams += [wrap(words[i-1:i+1]), wrap(words[i:i+2])]
   else:
     for j in range(max_ngrams):
        ngrams += [wrap(words[i+j-max_ngrams+1:i+j+1])]
     get_ngrams(words, i, max_ngrams-1, ngrams)

def main():
  scored = open(sys.argv[1], 'r')
  
  #onegrams = {}
  frequency = {}
  line = scored.readline()
  while line != '':
    possibilities = []
    
    # there's an empty line between each group of lines in scored
    while line != '\n':
      possibilities.append(line)
      line = scored.readline()
    
    # get ambiguous indices 
    #ambiguous_indices = possibilities.pop(0).split(',')
    
    # to get the defaults
    #for line in possibilities:
    #  try: line = line.lower()
    #  except: pass

    #  words = line.split('$ ^')
    #  for i, word in enumerate(words):
    #    if i in ambiguous_indices:
    #      sl, tl = word.split('/')
    #      if sl not in onegrams:
    #        onegrams[sl] = {}

    #      if tl not in onegrams[sl]:
    #        onegrams[sl][tl] = prob
    #      else:
    #        onegrams[sl][tl] += prob  

    # getting n-grams
    ambiguous = get_ambiguous(possibilities)
    for line in possibilities:
      try: line = line.lower()
      except: pass
      
      prob = float(line.split('\t')[0]) # subject to change
      line = line.split('\t')[2]
      tokens = [word for word in line.split('$ ^')]

      for i in range(len(tokens)):
        if tokens[i] in ambiguous:
          # max ngrams has to come from somewhere
          max_ngrams = 5
          ngrams = []
          get_ngrams(tokens, i, max_ngrams, ngrams)
          
          split = tokens[i].split('/')
          sl, tl = split[0], split[1]

          insert_ngrams(ngrams, frequency, sl, tl, prob) 
    line = scored.readline()


  # getting defaults
  #defaults = {}
  #for sl in onegrams:
  #  highest = 0
  #  for tl in onegrams[sl]:
  #    if onegrams[sl][tl] > highest:
  #      highest = onegrams[sl][tl]
  #      default = tl
  #  defaults[sl] = default

  # printing n-grams
  #for word in frequency:
  #  for ngram in frequency[word]:
  #    print('{}\t{}\t{}'.format(word, ngram, frequency[word][ngram]))

  for sl in frequency:
    for ngram in frequency[sl]:
      total, max_freq = 0, 0
      for tl in frequency[sl][ngram]:
        if frequency[sl][ngram][tl] > max_freq:
          max_freq = frequency[sl][ngram][tl]
          max_tl = tl
        total += frequency[sl][ngram][tl]
      
      crisp = str(frequency[sl][ngram][max_tl]/total)
      # printing output of ngram-pruning-frac.py
      print('\t'.join([crisp, str(max_freq), ngram, sl, max_tl]))

if __name__ == "__main__":
  main()
