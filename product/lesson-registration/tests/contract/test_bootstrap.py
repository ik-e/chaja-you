import unittest
import dev


class CandidateBoundary(unittest.TestCase):
    def test_dependency_replay(self):
        dev.check_package("common")
