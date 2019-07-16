import kenlm
import sys
import re
import os
from subprocess import check_output, Popen, PIPE, run
from collections import deque

class Scorer:
    def __init__(self, binary_model):
        self.probabilities = []
        try:
            # create language model
            self.model = kenlm.LanguageModel(binary_model)
            self.max_ngram = self.model.order
        except:
            print('Error: loading of language model failed.')
            sys.exit(1)
    
    def get_probability(self, tokens):
        ngram = deque() # should behave as a queue

        # trim each token
        for i in range(len(tokens)): tokens[i] = self.trim(tokens[i])
       
        if len(tokens) > self.max_ngram:
          # first put an n-gram in the queue
          for i in range(self.max_ngram): ngram.append(tokens[i])
       
          probability = 0
          for i in range(self.max_ngram, len(tokens)):
              # get the probability of n-gram
              probability += self.model.score(' '.join(list(ngram)))
              ngram.popleft() # pop front
              ngram.append(tokens[i]) # push back a new word

        else: # len(tokens) <= self.max_ngram
            probability = self.model.score(' '.join(tokens))

        return probability
    
    def trim(self, string):
        # remove white space and unknown words (really just *?)
        return re.sub('[\n\t\v\f\r *]', '', string)
    
    def print_results(self):
        if self.probabilities:
            for tup in self.probabilities:
                prob = '{:5f}'.format(tup[0])
                line = tup[1].strip('\n')
                print(prob + '\t' + line)
            print()
    
    def normalize_probabilities(self):
        # norm = sum of all probs
        norm = sum([prob for (prob, _) in self.probabilities])

        # divide each prob by norm
        for i in range(len(self.probabilities)):
            self.probabilities[i][0] /= norm
    
    def fractional(self, corpus_file, transducer, lang_pair):
        # progress bar things
        cmd = ['wc', '-l', corpus_file]
        corpus_length = int(check_output(cmd).split()[0])
        progress = 0

        # 1) create process for getting tagged trimmed version of corpus
        #cmd = ['apertium', '-d', transducer, lang_pair + '-expand-tagged']
        #tt = Popen(cmd, stdin=PIPE, stdout=PIPE, universal_newlines=True)

        # 2) create process for generating line so we can get n-gram probs
        #cmd = ['apertium', '-d', transducer, lang_pair + '-gen-ambig']
        #gen = Popen(cmd, stdin=PIPE, stdout=PIPE, universal_newlines=True)

        with open(corpus_file, 'r') as corpus:
          line = corpus.readline()
          while line != '':
            # 1) get tagged trimmed version of corpus
            cmd = ['apertium', '-d', transducer, lang_pair + '-expand-tagged']
            tt = run(cmd, input=line, stdout=PIPE, universal_newlines=True)
            tt_lines = tt.stdout.split('\n')

            # len of 1 means line is not ambiguous, so we shouldn't move on
            if len(tt_lines) == 1:
              line = corpus.readline()
              progress += 1
              continue

            # 2) generate line so we can get n-gram probs
            cmd = ['apertium', '-d', transducer, lang_pair + '-gen-ambig']
            gen = run(cmd, input=line, stdout=PIPE, universal_newlines=True)
            gen_lines = gen.stdout.strip().split('\n')

            for i, possibility in enumerate(gen_lines):
              tokens = possibility.split()[2:] # removing nums
              prob = self.get_probability(tokens)
              to_write = str(progress) + tt_lines[i][1:] # get rid of first num
              self.probabilities.append([prob, to_write])

            # setting up for the next line to be read
            self.normalize_probabilities()
            self.print_results()
            self.probabilities.clear()
            
            if progress % 10 == 0:
              progress_bar(progress, corpus_length)

            # reading next line
            line = corpus.readline()
            progress += 1

def progress_bar(progress, length):
    percentage = '{:.1f}'.format(100*progress/length)
    stars = int(50*progress/length)
    ratio = str(progress) + '/' + str(length)
    out = '[{}{}] {}% {}'.format(stars*'*', (50-stars)*'-', percentage, ratio)
    print(out, file=sys.stderr, end='\r')

def main():
    if len(sys.argv) != 5:
        print("Error: wrong number of arguments.")
        print("Usage: score.py <corpus> <binary-kenlm> <transduc> <lang pair>")
        sys.exit(1)
    
    scorer = Scorer(sys.argv[2])
    scorer.fractional(sys.argv[1], sys.argv[3], sys.argv[4])
    
if __name__ == "__main__":
    main()
