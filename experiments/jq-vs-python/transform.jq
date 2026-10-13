(.accounts | map(select(.status == "active")) | INDEX(.id)) as $accounts
| [ .events[]
    | select($accounts[.account_id] != null)
    | . as $event
    | $accounts[.account_id] as $account
    | {
        id: $account.id,
        name: $account.name,
        region: $account.region,
        tags: $account.tags,
        category: $event.category,
        amount: $event.amount
      }
  ]
| group_by(.id)
| map({
    id: .[0].id,
    name: .[0].name,
    region: .[0].region,
    tags: .[0].tags,
    event_count: length,
    total_amount: (map(.amount) | add),
    categories: (map(.category) | unique | sort)
  })
| sort_by(-.total_amount, .id)
| .[:50]
