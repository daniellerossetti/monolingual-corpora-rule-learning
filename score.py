import kenlm
import sys
import re
import queue
from threading import Thread, Barrier, Lock
from subprocess import check_output, Popen, PIPE, run
from collections import deque

class Scorer:
    def __init__(self, binary_model, transducer, lang_pair):
        self.transducer = transducer
        self.lang_pair = lang_pair
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
            self.probabilities.sort(key=lambda x: x[2])
            for (prob, number, subnumber, line) in self.probabilities:
                out = ['{:5f}'.format(prob)]
                out += [str(number) + ' ' + str(subnumber)]
                out += [line.strip('\n')]
                print('\t'.join(out))
            print()
    
    def normalize_probabilities(self):
        # norm = sum of all probs
        norm = sum([prob for (prob, _, _, _) in self.probabilities])

        # divide each prob by norm
        for i in range(len(self.probabilities)):
            self.probabilities[i][0] /= norm
    
    def fractional(self, corpus_file):
        # progress bar things
        cmd = ['wc', '-l', corpus_file]
        corpus_length = int(check_output(cmd).split()[0])
        progress = 0
        
        #cmd = ['apertium', '-d', self.transducer, self.lang_pair + '-expand-tagged']
        #tt = Popen(cmd, stdin=PIPE, stdout=PIPE, universal_newlines=True)

        #cmd = ['apertium', '-d', self.transducer, self.lang_pair + '-gen-ambig']
        #gen = Popen(cmd, stdin=PIPE, stdout=PIPE, universal_newlines=True)

        with open(corpus_file, 'r') as corpus:
          line = corpus.readline()
          while line:
            tt_lines, gen_lines = [], []
            # 1) gets tagged trimmed version of corpus
            tt_thread = Thread(args=(line, tt_lines), target=self.tagged_trimmed)
            # 2) generate line so we can get n-gram probs
            gen_thread = Thread(args=(line, gen_lines), target=self.generated)

            # begin and end
            tt_thread.start()
            gen_thread.start()
            tt_thread.join()
            gen_thread.join()
            
            # means line is not ambiguous, move on to next line
            if len(tt_lines) == 1:
              line = corpus.readline()
              progress += 1
              continue

            threads = []
            self.barrier = Barrier(len(gen_lines)-1)
            for i in range(len(gen_lines)):
              args = (gen_lines[i], tt_lines[i], progress)
              t = Thread(args=args, target=self.all_possibilities)
              t.start()
              threads.append(t)
            
            # -------------------------------
            # hack since barrier.wait() hangs
            if not self.barrier.n_waiting:
              try:
                self.barrier.abort()
              except BrokenBarrierError:
                for t in threads:
                  t.join()
            # -------------------------------
            
            # setting up for the next line to be read
            self.normalize_probabilities()
            self.print_results()
            self.probabilities.clear()

            # reading next line
            line = corpus.readline()
            progress += 1
                        
            progress_bar(progress, corpus_length) 

    def tagged_trimmed(self, line, tt_lines):
      cmd = ['apertium', '-d', self.transducer, self.lang_pair + '-expand-tagged']
      tt = run(cmd, input=line, stdout=PIPE, universal_newlines=True)
      for res in tt.stdout.split('\n'):
        tt_lines.append(res)

    def generated(self, line, gen_lines):
      cmd = ['apertium', '-d', self.transducer, self.lang_pair + '-gen-ambig']
      gen = run(cmd, input=line, stdout=PIPE, universal_newlines=True)
      for res in gen.stdout.strip().split('\n'):
        gen_lines.append(res)

    def all_possibilities(self, gen_line, tt_line, progress):
        tokens = gen_line.split()[2:] # removing nums
        prob = self.get_probability(tokens)
        # get rid of first num
        subnumber = int(tt_line.split('\t')[0].split()[1])
        line = ' '.join(tt_line.split()[2:])
        self.probabilities.append([prob, progress, subnumber, line])

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
    
    scorer = Scorer(sys.argv[2], sys.argv[3], sys.argv[4])
    scorer.fractional(sys.argv[1])
    
if __name__ == "__main__":
    main()
