from __future__ import annotations
import json, sys

def transform(doc):
    accounts={a['id']:a for a in doc['accounts'] if a['status']=='active'}
    grouped={}
    for event in doc['events']:
        account=accounts.get(event['account_id'])
        if account is None:
            continue
        row=grouped.get(account['id'])
        if row is None:
            row={
                'id':account['id'],
                'name':account['name'],
                'region':account['region'],
                'tags':account['tags'],
                'event_count':0,
                'total_amount':0,
                'categories':set(),
            }
            grouped[account['id']]=row
        row['event_count'] += 1
        row['total_amount'] += event['amount']
        row['categories'].add(event['category'])
    rows=[]
    for row in grouped.values():
        row['categories']=sorted(row['categories'])
        rows.append(row)
    rows.sort(key=lambda row:(-row['total_amount'],row['id']))
    return rows[:50]

def main():
    doc=json.load(sys.stdin)
    json.dump(transform(doc),sys.stdout,separators=(',',':'),sort_keys=True)
    sys.stdout.write('\n')

if __name__=='__main__':
    main()
