import kenlm
import sys
import re
from collections import deque

class Ranker:
    def __init__(self, filename):
        self.probabilities = []
        try:
            # create language model
            self.model = kenlm.LanguageModel(filename)
            # get ngram size
            self.max_ngram = self.model.order
            # Find out-of-vocabulary words
            #for w in words:
            #    if not w in model:
            #        print('"{0}" is an OOV'.format(w))
            # set significant decimal point
        except:
            print('Error: loading of language model failed.')
            sys.exit(1)
    
    def parse_line(self, line):
        # make a list out of the sentence
        tokens = line.split()
        # remove .[][ from beginning
        tokens.pop(0)
        # remove ].[] from subline number 
        tokens[0] = int(tokens[0].strip('].[]'))
        return tokens
    
    def get_probability(self, tokens):
        ngram = deque() # should behave as a queue
        # trim each token
        for i in range(len(tokens)): tokens[i] = self.trim(tokens[i])
        # first put an n-gram in the queue
        for i in range(len(self.max_ngram)): ngram.append(tokens[i])
       
        if len(tokens) > self.max_ngram:
            probability = 0
            for i in range(len(self.max_ngram), len(tokens)):
                # get the probability of n-gram
                probability += self.model.score(" ".join(list(ngram)))
                # pop front and push back a new word
                ngram.popleft()
                ngram.append(tokens[i])
        else:
            probability = self.model.score(" ".join(tokens))
        return probability
    
    def trim(self, input):
        # remove white space and unknown words (really just *?)
        return re.sub('[\n\t\v\f\r *]', '', input)
    
    def print_results(self):
        if self.probabilities:
            # sort them by probability ranking order
            self.probabilities.sort()
            for i, tup in enumerate(self.probabilities):
                # rank, prob, line
                print('\t'.join([str(i), str(tup[0]), str(tup[1].strip('\n'))
            print()
    
    def normalize_probabilities(self):
        # norm = sum of all probs
        norm = 0
        for (prob, _) in self.probabilities: norm += prob
        # divide each prob by norm
        for (prob, _) in self.probabilities: prob = prob/norm
    
    def fractional(self):
        for line in sys.stdin:
            if len(line): # because last line in file can be empty
                tokens = self.parse_line(line)
                if tokens.pop(0) == 0: # line num
                    self.normalize_probabilities()
                    self.print_results()
                    self.probabilities.clear()
                prob = self.get_probability(tokens)
                self.probabilities.append((prob, line))
        self.normalize_probabilities()
        self.print_results()
    
# Check that total full score = direct score
def score(s):
     return sum(prob for prob, _, _ in model.full_scores(s))

def main():
    if len(sys.argv) != 2:
        print("Error: wrong number of arguments.")
        print("Usage: ranking.py <kenlm-binary-lm-file>")
        sys.exit(1)
    
    ranker = Ranker(sys.argv[1])
    ranker.fractional()
    
if __name__ == "__main__":
    main()
"""
    sentence = 'language modeling is fun .'
    print(sentence)
    print(model.score(sentence))

    assert (abs(score(sentence) - model.score(sentence)) < 1e-3)

    # Show scores and n-gram matches
    words = ['<s>'] + sentence.split() + ['</s>']
    for i, (prob, length, oov) in enumerate(model.full_scores(sentence)):
        print('{0} {1}: {2}'.format(prob, length, ' '.join(words[i+2-length:i+2])))
        if oov:
            print('\t"{0}" is an OOV'.format(words[i+1]))
"""
