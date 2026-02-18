import builtins
import os
from types import SimpleNamespace
from PIL import Image
import io

import pytest

import samus_manus_mvp.hands as hands


def test_move_simulated():
    hands.pyautogui = None
    res = hands.move(100, 200, 0.1)
    assert '(sim) move to (100,200)' in res


def test_click_simulated():
    hands.pyautogui = None
    res = hands.click(10, 20, button='left')
    assert '(sim) click at (10,20)' in res


def test_type_simulated():
    hands.pyautogui = None
    res = hands.type_text('hello', interval=0.01)
    assert "(sim) type: 'hello'" == res


class FakePyAutoGui:
    def __init__(self):
        self.move_calls = []
        self.click_calls = []
        self.write_calls = []

    def moveTo(self, x, y, duration=0):
        self.move_calls.append((x, y, duration))

    def click(self, x, y, button='left'):
        self.click_calls.append((x, y, button))

    def write(self, text, interval=0.02):
        self.write_calls.append((text, interval))

    def screenshot(self, out=None):
        # return a PIL Image object with save capability
        return Image.new('RGB', (2, 2), color='white')

    class Loc:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    def locateCenterOnScreen(self, img, confidence=None):
        return FakePyAutoGui.Loc(5, 6)


def test_move_with_pyautogui_fake(tmp_path):
    fake = FakePyAutoGui()
    hands.pyautogui = fake
    res = hands.move(7, 8, 0.0)
    assert 'moved to (7,8)' in res
    assert fake.move_calls

    res = hands.click(1, 2, button='right')
    assert 'clicked at (1,2)' in res
    assert fake.click_calls

    res = hands.type_text('ok', interval=0.01)
    assert "typed: 'ok'" in res
    assert fake.write_calls

    out = tmp_path / 'screen.png'
    sval = hands.screenshot(str(out))
    assert str(out) == sval

    # find-click
    res = hands.find_click('some.png', confidence=0.8, do_click=False, timeout=0.1)
    assert 'found' in res


def test_find_click_no_pyautogui():
    hands.pyautogui = None
    res = hands.find_click('img.png')
    assert '(sim) find' in res
