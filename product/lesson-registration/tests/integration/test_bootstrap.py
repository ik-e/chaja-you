import unittest
import dev


class BootstrapIntegration(unittest.TestCase):
    def test_fixture_and_local_mock_wiring(self):
        dev.smoke()
