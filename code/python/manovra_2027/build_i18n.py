import json,sys
sys.path.insert(0,'/home/claude/emend/src')
from i18n_a import T as A
from i18n_b import T as B
from i18n_c import T as C
from i18n_d import T as Dd
from i18n_e import T as E
raw={**A,**B,**C,**Dd,**E}
json.dump(raw,open('/tmp/claude-0/b/raw.json','w'),ensure_ascii=False)
print(len(raw))
