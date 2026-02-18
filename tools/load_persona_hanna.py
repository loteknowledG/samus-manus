from samus_manus_mvp.memory import get_memory

with open('persona-hanna.md', 'r', encoding='utf-8') as f:
    persona_text = f.read().strip()

mid = get_memory().add('persona', persona_text, metadata={'source': 'persona-hanna.md', 'age': 26})
print('added_id', mid)

personas = [m for m in get_memory().all(20) if m['type'] == 'persona']
print('most recent persona (top 3):')
for p in personas[:3]:
    print('-', p['id'], p['created_at'], p['text'].splitlines()[0][:120])
