from __future__ import annotations
import json, random
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
CATEGORIES=['build','deploy','query','read','write','sync','test','transform']
REGIONS=['na','eu','apac','latam']
TAGS=['alpha','beta','critical','edge','internal','public','batch','realtime']

def make(name: str, account_count: int, event_count: int, seed: int):
    rng=random.Random(seed)
    accounts=[]
    for i in range(account_count):
        accounts.append({
            'id':f'a{i:06d}',
            'name':f'Account {i:06d}',
            'status':'active' if i % 5 != 0 else 'disabled',
            'region':REGIONS[i % len(REGIONS)],
            'tags':sorted(rng.sample(TAGS, k=2 + (i % 3))),
        })
    events=[]
    for i in range(event_count):
        aid=rng.randrange(account_count)
        events.append({
            'account_id':f'a{aid:06d}',
            'category':CATEGORIES[rng.randrange(len(CATEGORIES))],
            'amount':rng.randrange(1,100_001),
            'timestamp':f'2026-10-{1+(i%13):02d}T{(i//13)%24:02d}:{(i*7)%60:02d}:00Z',
        })
    path=DATA/f'{name}.json'
    path.write_text(json.dumps({'accounts':accounts,'events':events},separators=(',',':'),sort_keys=True)+'\n',encoding='utf-8')
    print(name, account_count, event_count, path.stat().st_size)

make('small',100,2_000,314159)
make('large',5_000,100_000,271828)
