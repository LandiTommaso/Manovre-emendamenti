import json, sys
sys.path.insert(0, '/home/claude/multi/src')
from i18n_multi import T
base = json.load(open('/home/claude/emend/site/i18n.json'))
for i, l in enumerate(['en', 'es', 'fr']):
    for k, v in T.items(): base[l][k] = v[i]
json.dump(base, open('/home/claude/multi/site2/i18n.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print({l: len(base[l]) for l in base})
