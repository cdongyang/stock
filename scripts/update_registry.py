import json

registry_path = '/Users/dy.chen/Personal/stock/events/memory-flash/analyzed_events.json'

with open(registry_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_events = [
    {
        'url': 'https://www.aljazeera.com/economy/2026/6/1/us-says-ban-on-ai-chip-shipments-applies-to-chinese-firms-outside-china',
        'title': '美国重申AI芯片出口禁令覆盖中国企业境外子公司，封堵监管漏洞',
        'date': '2026-06-01',
        'file': 'events/memory-flash/events/2026-06-01_us-chip-ban-extends-chinese-firms-outside-china.md',
        'impact_rating': 'High Negative (China AI) / Low Impact (Western memory makers)',
        'analyzed_at': '2026-06-02T08:00:00Z'
    },
    {
        'url': 'https://news.samsung.com/global/samsung-ships-industry-first-commercial-hbm4-with-ultimate-performance-for-ai-computing',
        'title': '三星率先完成商业HBM4量产出货：传输速率11.7Gbps，全球首发',
        'date': '2026-06-01',
        'file': 'events/memory-flash/events/2026-06-01_samsung-ships-first-commercial-hbm4.md',
        'impact_rating': 'High Positive',
        'analyzed_at': '2026-06-02T08:00:00Z'
    }
]

existing_urls = set(e['url'] for e in data['events'])
added = 0
for ev in new_events:
    if ev['url'] not in existing_urls:
        data['events'].append(ev)
        added += 1

with open(registry_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added} events. Total: {len(data['events'])}")
