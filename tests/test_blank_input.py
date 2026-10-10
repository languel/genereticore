import unittest
import numpy as np
from PIL import Image
from genereticore.image.blank import is_blank


class BlankInputTests(unittest.TestCase):
    def test_uniform_backgrounds_and_small_marks(self):
        for color in ('white', 'black', '#8199aa'):
            self.assertTrue(is_blank(Image.new('RGB', (512, 512), color)))
        pixels = np.full((512, 512, 3), 255, dtype=np.uint8)
        pixels[240, 240] = 0
        self.assertFalse(is_blank(Image.fromarray(pixels)))
        pixels[240, 240] = 251
        self.assertFalse(is_blank(Image.fromarray(pixels)))

    def test_tolerates_only_tiny_background_noise(self):
        pixels = np.full((16, 16, 3), 255, dtype=np.uint8)
        pixels[4, 4] = 252
        self.assertTrue(is_blank(Image.fromarray(pixels)))
