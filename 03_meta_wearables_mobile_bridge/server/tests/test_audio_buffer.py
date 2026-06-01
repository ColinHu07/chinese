import unittest

import numpy as np

from audio_buffer import decode_pcm_frame


class AudioBufferTests(unittest.TestCase):
    def test_decode_int16_pcm(self):
        payload = np.array([0, 16_384, -16_384], dtype="<i2").tobytes()
        audio = decode_pcm_frame(payload, "int16")
        np.testing.assert_allclose(audio, np.array([0.0, 0.5, -0.5], dtype=np.float32), atol=1e-4)

    def test_decode_float32_pcm(self):
        payload = np.array([0.0, 0.25, -0.25], dtype="<f4").tobytes()
        audio = decode_pcm_frame(payload, "float32")
        np.testing.assert_allclose(audio, np.array([0.0, 0.25, -0.25], dtype=np.float32), atol=1e-6)


if __name__ == "__main__":
    unittest.main()
