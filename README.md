# Generating lexical-selection rules from monolingual corpora
This page describes how to generate lexical selection rules without relying on a parallel corpus. 
## Pre-requisites
- apertium-lex-tools (for now it's needed for multitrans)
- kenlm and a binary kenlm target language model
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
Using ```score.py``` creates a very, very large file. It is recommended that these three scripts are used as a pipeline:
```
python3 score.py <corpus> <binary-kenlm-model> <transducer-path> <language-pair> | python3 count.py | python3 create.py > example.rules
lrx-comp example.rules.lrx example.rules.lrx.bin
```
## How to create -expanded-tagged and -gen-ambig modes
```
<mode name="en-pt-expand-tagged" install="yes">
    <pipeline>
      <program name="lt-proc">
        <file name="en-pt.automorf.bin"/>
      </program>
      <program name="apertium-tagger -g $2">
        <file name="en-pt.prob"/>
      </program>
      <program name="new_multitrans -m -t">
        <file name="en-pt.autobil.bin"/>
      </program>
    </pipeline>
  </mode>
  
  <mode name="en-pt-expand-tagged" install="yes">
    <pipeline>
      <program name="lt-proc">
        <file name="en-pt.automorf.bin"/>
      </program>
      <program name="apertium-tagger -g $2">
        <file name="en-pt.prob"/>
      </program>
      <program name="new_multitrans -m">
        <file name="en-pt.autobil.bin"/>
      </program>
    </pipeline>
  </mode>
```

