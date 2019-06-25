import kenlm
import sys

class Ranker:
    def __init__(self, filename):
        #do try and pass
        # create language model
        model = kenlm.LanguageModel(filename)
        # get ngram size
        max_ngram = model.order
        # Find out-of-vocabulary words
        #for w in words:
        #    if not w in model:
        #        print('"{0}" is an OOV'.format(w))
        # set significant decimal point
    
    def parse_line(self, line):
        # remove ].[] from subline number 
        # don't want to add .[][ from beginning
        # make a list out of the sentence
        # return tokens
        pass
    
    def get_probability(self, tokens):
        # deque
        # trim each token
        # first put an n-gram in the queue
        # go through each element of tokens (pop front & push new back)
        #       create n-gram object
        #       get the probability of n-gram
        # return probability
        pass
    
    def trim(self, input):
        # remove white space and unknown words (really just *?)
        return input.translate(input.maketrans('', '', ), '\n\t\v\f\r *')
    
    def print_results(self):
        if not self.probabilities.empty():
            # sort them by probability ranking order
            sorted_probs = self.probabilities.sort()
            for i, prob in enumerate(sorted_probs):
                # rank, prob, line
                print(i + '\t' + sorted_probs[i][0] + '\t' + sorted_probs[i][1])
        print()
    
    def normalize_probabilities(self):
        # norm = sum of all probs
        norm = 0
        for prob in self.probabilities: norm += prob
        # divide each prob by norm
        for prob in self.probabilities: prob = prob/norm
    
    def fractional(self):
        for line in sys.stdin:
            if len(line): # because last line in file can be empty
                tokens = self.parse_line(line)
                if tokens.pop(0) == 0: # line num
                    self.normalize_probabilities()
                    self.print_results()
                    self.probabilities.clear()
                tokens.remove
                prob = self.get_probability(tokens)
                self.probabilities((prob, line))
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

    #Stateful query
    state = kenlm.State()
    state2 = kenlm.State()
    #Use <s> as context.  If you don't want <s>, use model.NullContextWrite(state).
    model.BeginSentenceWrite(state)
    accum = 0.0
    accum += model.BaseScore(state, "a", state2)
    accum += model.BaseScore(state2, "sentence", state)
    #score defaults to bos = True and eos = True.  Here we'll check without the end
    #of sentence marker.  
    assert (abs(accum - model.score("a sentence", eos = False)) < 1e-3)
    accum += model.BaseScore(state, "</s>", state2)
    assert (abs(accum - model.score("a sentence")) < 1e-3)
    """
