import sys

threshold = 0.9
ngrams =

print('<rules>')
ruleno = 0
for line in sys.stdin.readlines():
    row = line.strip().split('\t')
    try:
    	weight = row[0] # aka crisp
    	prob = row[1]
    	ngram = row[2]
    	sl = row[3]
    	tl = row[4]
    except:
	continue
	
    tl_lema = tl.split('<')[0].lower()
    tl_tags = '<'.join(tl.split('<')[1:]).replace('><', '.').replace('>', '')

    if float(weight) <= float(threshold): continue 
    if any([x.startswith("*") for x in ngram.split('$ ^')]): continue
    if any([x.startswith("^*") for x in ngram.split('$ ^')]): continue

    print('  <rule c="' + str(ruleno) + ': ' + prob + '" weight="' + weight + '">');
    ngram = ngram.split('$ ^')
    ngram[0] = ngram[0].strip('^')
    
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
