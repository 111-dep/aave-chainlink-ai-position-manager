from web3 import Web3
from web3.middleware import geth_poa_middleware
from config.config import PROVIDER_URL, PRIVATE_KEY, WALLET_ADDRESS

def get_web3_connection():
    """
    Establish a connection to the Ethereum network.
    
    Returns:
        Web3: A Web3 instance connected to the provider.
    """
    web3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
    
    # Add PoA middleware for networks like Polygon
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    if not web3.is_connected():
        raise ConnectionError(f"Failed to connect to provider at {PROVIDER_URL}")
    
    return web3

def get_account():
    """
    Get the account object from the private key.
    
    Returns:
        Account: The account object.
    """
    web3 = get_web3_connection()
    account = web3.eth.account.from_key(PRIVATE_KEY)
    return account

def get_nonce():
    """
    Get the current nonce for the wallet address.
    
    Returns:
        int: The current nonce.
    """
    web3 = get_web3_connection()
    return web3.eth.get_transaction_count(WALLET_ADDRESS)

def sign_and_send_transaction(transaction):
    """
    Sign and send a transaction.
    
    Args:
        transaction (dict): The transaction to sign and send.
        
    Returns:
        str: The transaction hash.
    """
    web3 = get_web3_connection()
    account = get_account()
    
    signed_tx = account.sign_transaction(transaction)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    return web3.to_hex(tx_hash)
