# Generating lexical-selection rules from monolingual corpora
This page describes how to generate lexical selection rules without relying on a parallel corpus. 
## Pre-requisites
- [apertium-lex-tools](https://github.com/apertium/apertium-lex-tools) (for now it's needed for multitrans)
- [kenlm](https://kheafield.com/code/kenlm/) and a binary kenlm target language model
- a language pair that has the following two modes: **-expand-tagged** and **-gen-ambig**
## Instructions
1 . Score all possible translations for each sentence using the language model:
```
python3 score.py <corpus> <binary-kenlm-model> <transducer-path> <language-pair> > example.scored
```
2. Count and score the n-grams surrounding ambiguous words:
```
cat example.scored | python3 count.py  > example.counted
```
3. Generate lexical selection rules:
```
cat example.counted | python3 create.py > example.rules
lrx-comp example.rules.lrx example.rules.lrx.bin
```
## Caution
Using ```score.py``` creates a very, very large file. Using 200,000 lines of corpora resulted in a 70GB output file. It is recommended that these three scripts are used as a pipeline:
```
python3 score.py <corpus> <binary-kenlm-model> <transducer-path> <language-pair> | python3 count.py | python3 create.py > example.rules
lrx-comp example.rules.lrx example.rules.lrx.bin
```
Expect this program to run for many hours. Using 200,000 lines of corpora, 
 - ```score.py``` took approximately 14 hours
 - ```count.py``` took approximately 3 hours
 - ```create.py``` took approximately 20 minutes
## How to create -expand-tagged and -gen-ambig modes
```
  <mode name="en-pt-expand-tagged" install="yes">
    <pipeline>
      <program name="lt-proc">
        <file name="en-pt.automorf.bin"/>
      </program>
      <program name="apertium-tagger -g $2">
        <file name="en-pt.prob"/>
      </program>
      <program name="multitrans -m -t -n -f">
        <file name="en-pt.autobil.bin"/>
      </program>
    </pipeline>
  </mode>

  <mode name="en-pt-gen-ambig" install="yes">
    <pipeline>
      <program name="lt-proc">
        <file name="en-pt.automorf.bin"/>
      </program>
      <program name="apertium-tagger -g $2">
        <file name="en-pt.prob"/>
      </program>
      <program name="multitrans -m -n -f">
        <file name="en-pt.autobil.bin"/>
      </program>
      <program name="apertium-pretransfer"/>
      <program name="apertium-transfer -b">
        <file name="apertium-en-pt.en-pt.t1x"/>
        <file name="en-pt.t1x.bin"/>
      </program>
      <program name="apertium-interchunk">
        <file name="apertium-en-pt.en-pt.t2x"/>
        <file name="en-pt.t2x.bin"/>
      </program>
      <program name="apertium-postchunk">
        <file name="apertium-en-pt.en-pt.t3x"/>
        <file name="en-pt.t3x.bin"/>
      </program>
      <program name="lt-proc -g">
        <file name="en-pt.autogen.bin"/>
      </program>
      <program name="lt-proc -p">
        <file name="en-pt.autopgen.bin"/>
      </program>
    </pipeline>
  </mode>
```

