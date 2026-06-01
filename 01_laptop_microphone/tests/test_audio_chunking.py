import unittest

import numpy as np

from recorder import RollingAudioBuffer, rms_energy, samples_for_seconds


class AudioChunkingTests(unittest.TestCase):
    def test_samples_for_seconds(self):
        self.assertEqual(samples_for_seconds(5, 16_000), 80_000)

    def test_rolling_buffer_keeps_recent_audio(self):
        buffer = RollingAudioBuffer(sample_rate=10, max_seconds=3)
        buffer.append(np.arange(20, dtype=np.float32))
        buffer.append(np.arange(20, 50, dtype=np.float32))
        np.testing.assert_array_equal(buffer.snapshot(), np.arange(20, 50, dtype=np.float32))

    def test_snapshot_seconds(self):
        buffer = RollingAudioBuffer(sample_rate=10, max_seconds=5)
        buffer.append(np.arange(50, dtype=np.float32))
        np.testing.assert_array_equal(buffer.snapshot(2), np.arange(30, 50, dtype=np.float32))

    def test_rms_energy_silence(self):
        self.assertEqual(rms_energy(np.zeros(160, dtype=np.float32)), 0.0)
        self.assertGreater(rms_energy(np.ones(160, dtype=np.float32) * 0.1), 0.09)


if __name__ == "__main__":
    unittest.main()
