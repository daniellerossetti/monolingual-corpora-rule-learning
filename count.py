# biltrans-extract-frac-freq.py + biltrans-count-patterns-ngrams.py + ngram-pruning-frac.py
import sys

not_wanted = ['<guio>', '<sent>', '<cm>', '^$', '*']

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
     for ngram in [wrap(words[i-1:i+1]), wrap(words[i:i+2])]:
       add = True
       for item in not_wanted:
         if item in ngram:
          add = False
       if add: ngrams += [ngram]
   else:
     for j in range(max_ngrams):
        add = True
        ngram = wrap(words[i+j-max_ngrams+1:i+j+1])
        for item in not_wanted:
          if item in ngram:
            add = False
        if add: ngrams += [ngram]
     get_ngrams(words, i, max_ngrams-1, ngrams)

def progress_bar(progress, length):
    percentage = '{:.1f}'.format(100*progress/length)
    stars = int(50*progress/length)
    ratio = str(progress) + '/' + str(length)
    out = '[{}{}] {}% {}'.format(stars*'=', (50-stars)*'-', percentage, ratio)
    print(out, file=sys.stderr, end='\r')

def main():
  frequency = {}
  line = sys.stdin.readline()
  progress = 0
  while line != '':
    possibilities = []
    
    # there's an empty line between each group of lines in scored
    while line != '\n':
      possibilities.append(line)
      line = sys.stdin.readline()
    
    # getting n-grams
    ambiguous = get_ambiguous(possibilities)
    for line in possibilities:
      try: line = line.lower()
      except: pass
      
      prob = float(line.split('\t')[0])
      line = line.strip().split('\t')[2]
      tokens = [token for token in line.split('$ ^')]

      # get only source language side of words
      words = [word.split('/')[0] for word in tokens]

      for i in range(len(tokens)):
        if tokens[i] in ambiguous:
          max_ngrams = 5 # has to come from somewhere
          ngrams = []
          get_ngrams(words, i, max_ngrams, ngrams)
          sl = words[i]
          tl = tokens[i].split('/')[1]
          insert_ngrams(ngrams, frequency, sl, tl, prob) 
    
    progress += 1
    progress_bar(progress, 200000)
    line = sys.stdin.readline()

  for sl in frequency:
    for ngram in frequency[sl]:
      freq_list  = [(tl, freq) for tl, frequency[sl][ngram][tl] in frequency[sl][ngram]]
      total = sum([freq for _, freq in freq_list])
      max_tl, max_freq = max(freq_list, key=lambda x: x[1])
      
      crisp = str(float(max_freq)/float(total))
      # printing output of ngram-pruning-frac.py
      print('\t'.join([crisp, str(max_freq), ngram.strip('\n'), sl, max_tl]))

if __name__ == "__main__":
  main()
