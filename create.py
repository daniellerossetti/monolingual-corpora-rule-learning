import sys

if len(sys.argv) != 2: 
  print('ngrams-to-rules.py <ngrams>')
  sys.exit(-1)

infile = open(sys.argv[1])
threshold = 1

print('<rules>')
ruleno = 0
for line in infile.readlines(): 
    row = line.strip().split('\t');
    
    weight = row[0] # aka crisp
    prob = row[1]
    ngram = row[2]
    sl = row[3]
    tl = row[4]
    tl_lema = tl.split('<')[0].lower();
    tl_tags = '<'.join(tl.split('<')[1:]).replace('><', '.').replace('>', '');

    # fix this -------------
    #if row[2].count('<guio>') > 0 or row[2].count('<sent>') > 0 or row[2].count('<cm>') > 0:
    #   print('PUNCTUATION_IN_PATTERN', line, file=sys.stderr)
    #   continue
    # ----------------------
    # fix this too ---------
    #if float(weight) <= float(threshold): 
    #   print("under threshold", weight, "<", threshold, "||",  line, file=sys.stderr)
    #   continue
    #------------------------
    if any([x.startswith("*") for x in ngram.split('$ ^')]): continue #unknown word in pattern

    print('  <rule c="' + str(ruleno) + ': ' + prob + '" weight="' + weight + '">');
    ngram = ngram.split('$ ^')
    words = []
    for word in ngram:
       words.append(word.split('/')[0])
    for word in words: 
        sl_lema = word.split('<')[0].lower()

        if '><' in word:
          sl_tags = '<'.join(word.split('<')[1:]).replace('><', '.').replace('>', '');
        else:
          sl_tags = '<'.join(word.split('<')[1:]).strip('<>');
    
        out = '    <match lemma="{}" tags="{}"><select lemma="{}" tags="{}"/></match>'
        print(out.format(sl_lema, sl_tags, tl_lema, tl_tags))
	  
    print('  </rule>')
    ruleno += 1

print('</rules>')
