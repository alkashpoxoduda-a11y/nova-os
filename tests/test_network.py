"""
Unit tests for NOVA OS Network Engine
"""

import unittest
from nova_os.network import NetworkManagerEngine

class TestNetworkEngine(unittest.TestCase):
    def setUp(self):
        self.net = NetworkManagerEngine()

    def test_list_interfaces(self):
        ifaces = self.net.list_interfaces()
        self.assertIsInstance(ifaces, list)

    def test_status(self):
        status = self.net.get_connection_status()
        self.assertIn("overall_state", status)
        self.assertIn("ip_address", status)

if __name__ == "__main__":
    unittest.main()
