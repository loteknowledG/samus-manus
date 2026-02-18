from PIL import Image
import os
import tempfile

import samus_manus_mvp.eyes as eyes


class FakePyAutoGui:
    def screenshot(self):
        return Image.new('RGB', (4, 4), 'white')


def test_capture_screenshot_with_pyautogui(tmp_path):
    fake = FakePyAutoGui()
    eyes.pyautogui = fake
    out = str(tmp_path / 'shot.png')
    res = eyes.capture_screenshot(out)
    assert os.path.exists(res)
    assert res.endswith('shot.png')


def test_find_on_screen_no_pyautogui():
    eyes.pyautogui = None
    assert eyes.find_on_screen('nope.png') is None
