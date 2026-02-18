import os
import tempfile

from samus_manus_mvp.samus_agent import fallback_plan, run_task
from samus_manus_mvp.memory import Memory


def test_fallback_plan_screenshot():
    actions = fallback_plan('Please take a screenshot')
    types = [a.get('type') for a in actions]
    assert 'screenshot' in types or 'done' in types


def test_run_task_records_action(tmp_path, monkeypatch):
    # Use a temporary memory DB to avoid polluting repo memory
    mem_path = tmp_path / 'mem.db'
    m = Memory(str(mem_path))

    # Monkeypatch the module-level get_memory used by samus_agent
    import samus_manus_mvp.samus_agent as agent
    monkeypatch.setattr(agent, 'get_memory', lambda: m)

    # Run a harmless task that triggers fallback planner (type + done)
    run_task('say hello unit test', apply=False, approve_each=False, max_steps=10)

    # Ensure a task record and at least one action was recorded
    rows = m.all(50)
    types = [r['type'] for r in rows]
    assert 'task' in types
    assert 'action' in types


def test_plan_with_persona_is_sent_to_openai(tmp_path, monkeypatch):
    # create temp memory with a persona
    mem_path = tmp_path / 'mem2.db'
    m = Memory(str(mem_path))
    m.add('persona', 'be concise and cautious')

    import samus_manus_mvp.samus_agent as agent
    monkeypatch.setattr(agent, 'get_memory', lambda: m)

    # fake openai client and capture messages
    called = {}

    class FakeResp:
        class Choice:
            message = type('M', (), {'content': '[]'})
        choices = [Choice()]

    def fake_create(model, messages, max_tokens, temperature):
        called['messages'] = messages
        return FakeResp()

    fake_chat = type('C', (), {'create': staticmethod(fake_create)})
    monkeypatch.setattr(agent, 'openai', type('O', (), {'ChatCompletion': fake_chat}))
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

    actions = agent.plan_with_openai('Take a screenshot')
    assert isinstance(actions, list)
    # ensure persona text was included in the prompt passed to OpenAI
    assert any('Persona: be concise and cautious' in m['content'] for m in called['messages'])

