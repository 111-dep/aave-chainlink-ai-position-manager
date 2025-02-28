import json
from web3 import Web3
from utils.web3_utils import get_web3_connection, sign_and_send_transaction, get_nonce
from config.config import (
    AAVE_LENDING_POOL_ADDRESS,
    AAVE_DATA_PROVIDER_ADDRESS,
    WALLET_ADDRESS,
    HEALTH_FACTOR_MIN
)

# ABI files would be stored in a separate directory
# For simplicity, we're using placeholder ABIs
LENDING_POOL_ABI = []  # Replace with actual ABI
DATA_PROVIDER_ABI = []  # Replace with actual ABI

class AaveManager:
    """
    Class to interact with Aave protocol for lending and borrowing operations.
    """
    
    def __init__(self):
        self.web3 = get_web3_connection()
        self.lending_pool = self.web3.eth.contract(
            address=self.web3.to_checksum_address(AAVE_LENDING_POOL_ADDRESS),
            abi=LENDING_POOL_ABI
        )
        self.data_provider = self.web3.eth.contract(
            address=self.web3.to_checksum_address(AAVE_DATA_PROVIDER_ADDRESS),
            abi=DATA_PROVIDER_ABI
        )
        self.wallet_address = self.web3.to_checksum_address(WALLET_ADDRESS)
    
    def get_user_account_data(self):
        """
        Get user account data from Aave.
        
        Returns:
            dict: User account data including health factor, collateral, debt, etc.
        """
        user_data = self.lending_pool.functions.getUserAccountData(self.wallet_address).call()
        
        return {
            'total_collateral_eth': user_data[0],
            'total_debt_eth': user_data[1],
            'available_borrow_eth': user_data[2],
            'current_liquidation_threshold': user_data[3],
            'ltv': user_data[4],
            'health_factor': user_data[5]
        }
    
    def get_health_factor(self):
        """
        Get the current health factor.
        
        Returns:
            float: The current health factor.
        """
        user_data = self.get_user_account_data()
        health_factor = user_data['health_factor'] / 1e18  # Convert from Wei
        return health_factor
    
    def is_position_safe(self):
        """
        Check if the position is safe from liquidation.
        
        Returns:
            bool: True if the position is safe, False otherwise.
        """
        health_factor = self.get_health_factor()
        return health_factor > HEALTH_FACTOR_MIN
    
    def deposit(self, asset_address, amount, referral_code=0):
        """
        Deposit assets to Aave.
        
        Args:
            asset_address (str): The address of the asset to deposit.
            amount (int): The amount to deposit in Wei.
            referral_code (int, optional): Referral code. Defaults to 0.
            
        Returns:
            str: The transaction hash.
        """
        asset_address = self.web3.to_checksum_address(asset_address)
        
        # Approve the lending pool to spend tokens
        # This would require the ERC20 ABI and approval transaction
        # For simplicity, we're skipping this step
        
        # Prepare the deposit transaction
        tx = self.lending_pool.functions.deposit(
            asset_address,
            amount,
            self.wallet_address,
            referral_code
        ).build_transaction({
            'from': self.wallet_address,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': get_nonce()
        })
        
        # Sign and send the transaction
        return sign_and_send_transaction(tx)
    
    def withdraw(self, asset_address, amount):
        """
        Withdraw assets from Aave.
        
        Args:
            asset_address (str): The address of the asset to withdraw.
            amount (int): The amount to withdraw in Wei.
            
        Returns:
            str: The transaction hash.
        """
        asset_address = self.web3.to_checksum_address(asset_address)
        
        # Prepare the withdraw transaction
        tx = self.lending_pool.functions.withdraw(
            asset_address,
            amount,
            self.wallet_address
        ).build_transaction({
            'from': self.wallet_address,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': get_nonce()
        })
        
        # Sign and send the transaction
        return sign_and_send_transaction(tx)
    
    def borrow(self, asset_address, amount, interest_rate_mode, referral_code=0):
        """
        Borrow assets from Aave.
        
        Args:
            asset_address (str): The address of the asset to borrow.
            amount (int): The amount to borrow in Wei.
            interest_rate_mode (int): 1 for stable, 2 for variable.
            referral_code (int, optional): Referral code. Defaults to 0.
            
        Returns:
            str: The transaction hash.
        """
        asset_address = self.web3.to_checksum_address(asset_address)
        
        # Prepare the borrow transaction
        tx = self.lending_pool.functions.borrow(
            asset_address,
            amount,
            interest_rate_mode,
            referral_code,
            self.wallet_address
        ).build_transaction({
            'from': self.wallet_address,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': get_nonce()
        })
        
        # Sign and send the transaction
        return sign_and_send_transaction(tx)
    
    def repay(self, asset_address, amount, interest_rate_mode):
        """
        Repay borrowed assets to Aave.
        
        Args:
            asset_address (str): The address of the asset to repay.
            amount (int): The amount to repay in Wei.
            interest_rate_mode (int): 1 for stable, 2 for variable.
            
        Returns:
            str: The transaction hash.
        """
        asset_address = self.web3.to_checksum_address(asset_address)
        
        # Approve the lending pool to spend tokens
        # This would require the ERC20 ABI and approval transaction
        # For simplicity, we're skipping this step
        
        # Prepare the repay transaction
        tx = self.lending_pool.functions.repay(
            asset_address,
            amount,
            interest_rate_mode,
            self.wallet_address
        ).build_transaction({
            'from': self.wallet_address,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': get_nonce()
        })
        
        # Sign and send the transaction
        return sign_and_send_transaction(tx)
