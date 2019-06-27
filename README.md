# Generating lexical-selection rules from monolingual corpora
This page describes how to generate lexical selection rules without relying on a parallel corpus. 
## Pre-requisites
- apertium-lex-tools (for now it's needed for multitrans)
- kenlm and a binary kenlm target language model
- a language pair that has the following two modes: **-multi** and **-pretransfer** (see apertium-mk-en/modes.xml if you want to recreate these modes in a language pair!)
## Instructions
1. Make a tagged version of your source language corpus:
```
cat <source-language-corpus> | apertium-destxt | apertium -f none -d /path/to/dir/of/language/pair <lang-pair>-pretransfer > <lang-pair>.tagged
```
2. Make an ambiguous version of your corpus and trim redundant tags:
```
cat <lang-pair>.tagged | /path/to/apertium-lex-tools/./multitrans /path/to/dir/of/language/pair/<lang-pair>.autobil.bin -b -f -t -n > <lang-pair>.ambig
```
3. Translate, score, and rank all possible disambiguation paths (**warning**: this will create a very large file. a corpus of 30MB with ~200,000 lines generated a 8GB file in this step):
```
cat <lang-pair>.tagged | /path/to/apertium-lex-tools/./multitrans /path/to/dir/of/language/pair/<lang-pair>.autobil.bin -m -f -n |
apertium -f none -d /path/to/dir/of/language/pair <lang-pair>-multi | python3 ranking.py /path/to/binary/lang/model > <lang-pair>.ranked
```
4. Now we have a pseudo-parallel corpus where each possible translation is scored. Extract a frequency lexicon and ngrams:
```
python3 counting.py <lang-pair>.ranked > <lang.pair>.freq
```
5. Align the tagged ambiguous version and the ranked version of the corpus so you know the tags:
```
python3 matching.py <lang-pair>.ambig <lang-pair>.ranked > <lang-pair>.aligned
```
6. Finally, we generate and compile lexical selection rules!
```
python3 creating.py <input-files> > <lang-pair>.rules
lrx-comp <lang-pair>.rules.lrx <lang-pair>.rules.lrx.bin
```
