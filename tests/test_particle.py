import unittest
from unittest.mock import patch, Mock
from particle import Particle
from pygame import Surface
from settings import ANIMATION_SPEED


class TestParticle(unittest.TestCase):
    def test_particle(self):
        srf = Surface((5, 5))
        with patch('particle.get_img', Mock(return_value={"land": [srf, 1, 2, ], "run": [srf, 1]})):
            with patch('particle.load_flipped', Mock(return_value={'run': [2, 3]})):
                p1 = Particle((0, 0), 'land')
                p2 = Particle((0, 0), 'run', flipped=True)

                p1.update(3)
                self.assertEqual(p1.frame_index, ANIMATION_SPEED)
                self.assertEqual(p1.rect.x, 3)
                self.assertEqual(p1.image, srf)

                p1.frame_index = 1
                p1.update(3)
                self.assertEqual(p1.rect.x, 6)
                self.assertEqual(p1.image, 1)

                p1.frame_index = 3
                p1.kill = Mock()
                p1.update(3)
                p1.kill.assert_called_once()

                p2.update(3)
                self.assertEqual(p2.frame_index, ANIMATION_SPEED)
                self.assertEqual(p2.rect.x, 0)
                self.assertEqual(p2.image, 2)
                p2.frame_index = 3
                p2.kill = Mock()
                p2.update(3)
                p2.kill.assert_not_called()
                self.assertEqual(p2.frame_index, 0)

                with patch('particle.ANIMATION_SPEED', 'str'):
                    self.assertRaises(TypeError, Particle, (0, 0), 'land')


if __name__ == '__main__':
    unittest.main()
