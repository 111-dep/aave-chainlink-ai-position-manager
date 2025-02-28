import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Blockchain Configuration
NETWORK = os.getenv("NETWORK", "ethereum")  # ethereum, polygon, etc.
PROVIDER_URL = os.getenv("PROVIDER_URL", "https://mainnet.infura.io/v3/your-infura-key")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1"))  # 1 for Ethereum mainnet

# Wallet Configuration
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

# Aave Configuration
AAVE_LENDING_POOL_ADDRESS = os.getenv("AAVE_LENDING_POOL_ADDRESS", "")
AAVE_DATA_PROVIDER_ADDRESS = os.getenv("AAVE_DATA_PROVIDER_ADDRESS", "")

# Chainlink Configuration
CHAINLINK_FEED_REGISTRY = os.getenv("CHAINLINK_FEED_REGISTRY", "")
PRICE_FEEDS = {
    "ETH/USD": os.getenv("ETH_USD_FEED", ""),
    "BTC/USD": os.getenv("BTC_USD_FEED", ""),
    # Add more price feeds as needed
}

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai, huggingface, etc.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")

# Position Management Configuration
LIQUIDATION_THRESHOLD_BUFFER = float(os.getenv("LIQUIDATION_THRESHOLD_BUFFER", "0.05"))  # 5% buffer
HEALTH_FACTOR_MIN = float(os.getenv("HEALTH_FACTOR_MIN", "1.5"))  # Minimum health factor
