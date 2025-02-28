import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chainlink_oracle import ChainlinkOracle

class TestChainlinkOracle(unittest.TestCase):
    """
    Test cases for the ChainlinkOracle class.
    """
    
    @patch('src.chainlink_oracle.get_web3_connection')
    @patch('src.chainlink_oracle.PRICE_FEEDS', {'ETH/USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'})
    def setUp(self, mock_get_web3_connection):
        """
        Set up the test environment.
        """
        self.mock_web3 = MagicMock()
        mock_get_web3_connection.return_value = self.mock_web3
        
        # Mock the contract
        self.mock_contract = MagicMock()
        self.mock_web3.eth.contract.return_value = self.mock_contract
        
        # Create the oracle
        self.oracle = ChainlinkOracle()
    
    def test_get_latest_price(self):
        """
        Test getting the latest price.
        """
        # Mock the latestRoundData function
        mock_function = MagicMock()
        self.mock_contract.functions.latestRoundData = mock_function
        mock_function.return_value.call.return_value = [1, 200000000000, 1000000000, 1000000000, 1]
        
        # Get the latest price
        price = self.oracle.get_latest_price('ETH/USD')
        
        # Check the price
        self.assertEqual(price, 2000.0)
    
    def test_get_all_prices(self):
        """
        Test getting all prices.
        """
        # Mock the latestRoundData function
        mock_function = MagicMock()
        self.mock_contract.functions.latestRoundData = mock_function
        mock_function.return_value.call.return_value = [1, 200000000000, 1000000000, 1000000000, 1]
        
        # Get all prices
        prices = self.oracle.get_all_prices()
        
        # Check the prices
        self.assertEqual(prices, {'ETH/USD': 2000.0})
    
    def test_get_price_feed_update_time(self):
        """
        Test getting the price feed update time.
        """
        # Mock the latestRoundData function
        mock_function = MagicMock()
        self.mock_contract.functions.latestRoundData = mock_function
        mock_function.return_value.call.return_value = [1, 200000000000, 1000000000, 1234567890, 1]
        
        # Get the update time
        update_time = self.oracle.get_price_feed_update_time('ETH/USD')
        
        # Check the update time
        self.assertEqual(update_time, 1234567890)
    
    def test_get_latest_price_invalid_pair(self):
        """
        Test getting the latest price for an invalid pair.
        """
        # Try to get the latest price for an invalid pair
        with self.assertRaises(ValueError):
            self.oracle.get_latest_price('INVALID/PAIR')

if __name__ == '__main__':
    unittest.main()
