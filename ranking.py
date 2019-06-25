import kenlm

class Ranker:
    def __init__(self, filename):
        #do try and pass
        # create language model
        # get ngram size
        # oov stuff
        # set significant decimal point
        pass
    
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
        # remove white space and unknown words
        pass
    
    def print_results(self):
        # if self.probabilities:
        #   print them out in ranking order by probability
        #   sort
        #   print i (rank), prob.first (prob), prob.second (line)
        # final \n
        pass
    
    def normalize_probabilities(self):
        # norm = adding all probs
        # divide each prob by norm
        pass
    
    def fractional(self):
        # while not the end of file:
        #   get line
        #   if len(line) #because last line in file is empty
        #       tokens = parse_line(line)
        #       if tokens[0] == 0
        #           normalize_probabilities
        #           print_results
        #           clear self.probs
        #       remove line num from tokens
        #       prob = this->get_probability(tokens)
        #       self.probs.((prob, line))
        #   normalize_probabilities
        #   print_results
    
# Check that total full score = direct score
def score(s):
     return sum(prob for prob, _, _ in model.full_scores(s))

def main():
    model = kenlm.LanguageModel(argv[1])
    print('{0}-gram model'.format(model.order))

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

    # Find out-of-vocabulary words
    for w in words:
        if not w in model:
            print('"{0}" is an OOV'.format(w))

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
