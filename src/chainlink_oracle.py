from web3 import Web3
from utils.web3_utils import get_web3_connection
from config.config import CHAINLINK_FEED_REGISTRY, PRICE_FEEDS

# ABI for Chainlink Price Feed
PRICE_FEED_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

class ChainlinkOracle:
    """
    Class to interact with Chainlink price feeds.
    """
    
    def __init__(self):
        self.web3 = get_web3_connection()
        self.price_feeds = {}
        
        # Initialize price feed contracts
        for pair, address in PRICE_FEEDS.items():
            if address:
                self.price_feeds[pair] = self.web3.eth.contract(
                    address=self.web3.to_checksum_address(address),
                    abi=PRICE_FEED_ABI
                )
    
    def get_latest_price(self, pair):
        """
        Get the latest price for a given pair.
        
        Args:
            pair (str): The trading pair, e.g., 'ETH/USD'.
            
        Returns:
            float: The latest price.
            
        Raises:
            ValueError: If the pair is not supported.
        """
        if pair not in self.price_feeds:
            raise ValueError(f"Price feed for {pair} not configured")
        
        price_feed = self.price_feeds[pair]
        
        # Get the latest round data
        round_data = price_feed.functions.latestRoundData().call()
        
        # Extract the price and convert it to a human-readable format
        # The price is usually returned with 8 decimals
        price = round_data[1] / 10**8
        
        return price
    
    def get_all_prices(self):
        """
        Get the latest prices for all configured pairs.
        
        Returns:
            dict: A dictionary mapping pairs to their latest prices.
        """
        prices = {}
        
        for pair in self.price_feeds:
            try:
                prices[pair] = self.get_latest_price(pair)
            except Exception as e:
                print(f"Error getting price for {pair}: {e}")
        
        return prices
    
    def get_price_feed_update_time(self, pair):
        """
        Get the timestamp of the last update for a given pair.
        
        Args:
            pair (str): The trading pair, e.g., 'ETH/USD'.
            
        Returns:
            int: The timestamp of the last update.
            
        Raises:
            ValueError: If the pair is not supported.
        """
        if pair not in self.price_feeds:
            raise ValueError(f"Price feed for {pair} not configured")
        
        price_feed = self.price_feeds[pair]
        
        # Get the latest round data
        round_data = price_feed.functions.latestRoundData().call()
        
        # Extract the updated at timestamp
        updated_at = round_data[3]
        
        return updated_at
