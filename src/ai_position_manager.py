import json
import time
import openai
import pandas as pd
import numpy as np
from config.config import (
    OPENAI_API_KEY, 
    AI_MODEL, 
    LIQUIDATION_THRESHOLD_BUFFER,
    HEALTH_FACTOR_MIN
)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

class AIPositionManager:
    """
    Class to manage positions using AI based on real-time data.
    """
    
    def __init__(self, aave_manager, chainlink_oracle):
        """
        Initialize the AI position manager.
        
        Args:
            aave_manager: An instance of AaveManager.
            chainlink_oracle: An instance of ChainlinkOracle.
        """
        self.aave_manager = aave_manager
        self.chainlink_oracle = chainlink_oracle
        self.price_history = {}
        self.position_history = []
        
    def collect_market_data(self):
        """
        Collect current market data from Chainlink oracles.
        
        Returns:
            dict: Current market data.
        """
        current_prices = self.chainlink_oracle.get_all_prices()
        timestamp = int(time.time())
        
        # Store price history for analysis
        for pair, price in current_prices.items():
            if pair not in self.price_history:
                self.price_history[pair] = []
            
            self.price_history[pair].append({
                'timestamp': timestamp,
                'price': price
            })
            
            # Keep only the last 1000 price points
            if len(self.price_history[pair]) > 1000:
                self.price_history[pair] = self.price_history[pair][-1000:]
        
        return current_prices
    
    def collect_position_data(self):
        """
        Collect current position data from Aave.
        
        Returns:
            dict: Current position data.
        """
        user_data = self.aave_manager.get_user_account_data()
        timestamp = int(time.time())
        
        position_data = {
            'timestamp': timestamp,
            'total_collateral_eth': user_data['total_collateral_eth'] / 1e18,
            'total_debt_eth': user_data['total_debt_eth'] / 1e18,
            'available_borrow_eth': user_data['available_borrow_eth'] / 1e18,
            'current_liquidation_threshold': user_data['current_liquidation_threshold'] / 10000,  # Convert from basis points
            'ltv': user_data['ltv'] / 10000,  # Convert from basis points
            'health_factor': user_data['health_factor'] / 1e18  # Convert from Wei
        }
        
        # Store position history for analysis
        self.position_history.append(position_data)
        
        # Keep only the last 1000 position data points
        if len(self.position_history) > 1000:
            self.position_history = self.position_history[-1000:]
        
        return position_data
    
    def prepare_data_for_ai(self):
        """
        Prepare data to be sent to the AI model.
        
        Returns:
            dict: Data prepared for AI analysis.
        """
        market_data = self.collect_market_data()
        position_data = self.collect_position_data()
        
        # Calculate price changes
        price_changes = {}
        for pair, history in self.price_history.items():
            if len(history) > 1:
                current_price = history[-1]['price']
                previous_price = history[-2]['price']
                price_change_pct = (current_price - previous_price) / previous_price * 100
                price_changes[pair] = price_change_pct
        
        # Calculate volatility (standard deviation of price changes)
        volatility = {}
        for pair, history in self.price_history.items():
            if len(history) > 10:  # Need at least 10 data points for meaningful volatility
                prices = [point['price'] for point in history[-10:]]
                volatility[pair] = np.std(prices) / np.mean(prices) * 100  # Coefficient of variation as percentage
        
        # Prepare the data structure for AI
        ai_data = {
            'current_prices': market_data,
            'price_changes_pct': price_changes,
            'volatility_pct': volatility,
            'position': position_data,
            'liquidation_threshold_buffer': LIQUIDATION_THRESHOLD_BUFFER,
            'health_factor_min': HEALTH_FACTOR_MIN,
            'timestamp': int(time.time())
        }
        
        return ai_data
    
    def get_ai_recommendation(self):
        """
        Get a recommendation from the AI model based on current data.
        
        Returns:
            dict: AI recommendation.
        """
        data = self.prepare_data_for_ai()
        
        # Convert data to a format suitable for the AI model
        prompt = self._create_prompt(data)
        
        try:
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an AI financial advisor specialized in DeFi position management. Your task is to analyze the provided market and position data and recommend actions to prevent liquidation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extract the recommendation
            recommendation_text = response.choices[0].message.content
            
            # Parse the recommendation
            recommendation = self._parse_recommendation(recommendation_text)
            
            return recommendation
        
        except Exception as e:
            print(f"Error getting AI recommendation: {e}")
            return {
                'action': 'none',
                'reason': f'Error: {str(e)}',
                'confidence': 0
            }
    
    def _create_prompt(self, data):
        """
        Create a prompt for the AI model.
        
        Args:
            data (dict): Data to include in the prompt.
            
        Returns:
            str: The prompt for the AI model.
        """
        prompt = f"""
        Please analyze the following DeFi position data and market conditions:
        
        Current Position:
        - Total Collateral (ETH): {data['position']['total_collateral_eth']}
        - Total Debt (ETH): {data['position']['total_debt_eth']}
        - Available Borrow (ETH): {data['position']['available_borrow_eth']}
        - Current Liquidation Threshold: {data['position']['current_liquidation_threshold']}
        - LTV: {data['position']['ltv']}
        - Health Factor: {data['position']['health_factor']}
        
        Market Data:
        """
        
        for pair, price in data['current_prices'].items():
            prompt += f"- {pair}: {price}"
            if pair in data['price_changes_pct']:
                prompt += f" (24h change: {data['price_changes_pct'][pair]:.2f}%)"
            if pair in data['volatility_pct']:
                prompt += f" (Volatility: {data['volatility_pct'][pair]:.2f}%)"
            prompt += "\n"
        
        prompt += f"""
        Parameters:
        - Liquidation Threshold Buffer: {data['liquidation_threshold_buffer']}
        - Minimum Health Factor: {data['health_factor_min']}
        
        Based on this information, please recommend one of the following actions:
        1. Add more collateral (specify amount and asset)
        2. Repay some debt (specify amount and asset)
        3. Withdraw collateral (specify amount and asset)
        4. Borrow more (specify amount and asset)
        5. No action needed
        
        For each recommendation, provide:
        - The specific action to take
        - The reason for the recommendation
        - Your confidence level (0-100%)
        
        Format your response as a JSON object with the following structure:
        {
            "action": "add_collateral|repay_debt|withdraw_collateral|borrow_more|none",
            "asset": "ETH|USDC|...",
            "amount": 0.0,
            "reason": "Your reasoning here",
            "confidence": 85
        }
        """
        
        return prompt
    
    def _parse_recommendation(self, recommendation_text):
        """
        Parse the recommendation text from the AI model.
        
        Args:
            recommendation_text (str): The recommendation text from the AI model.
            
        Returns:
            dict: The parsed recommendation.
        """
        try:
            # Try to extract JSON from the response
            start_idx = recommendation_text.find('{')
            end_idx = recommendation_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = recommendation_text[start_idx:end_idx]
                recommendation = json.loads(json_str)
                
                # Validate the recommendation
                required_keys = ['action', 'reason', 'confidence']
                if not all(key in recommendation for key in required_keys):
                    raise ValueError("Missing required keys in recommendation")
                
                # If action is not 'none', asset and amount are required
                if recommendation['action'] != 'none' and ('asset' not in recommendation or 'amount' not in recommendation):
                    raise ValueError("Missing asset or amount for action")
                
                return recommendation
            else:
                raise ValueError("Could not find JSON in response")
        
        except Exception as e:
            print(f"Error parsing recommendation: {e}")
            print(f"Raw recommendation text: {recommendation_text}")
            
            # Return a default recommendation
            return {
                'action': 'none',
                'reason': f'Error parsing recommendation: {str(e)}',
                'confidence': 0
            }
    
    def execute_recommendation(self, recommendation):
        """
        Execute the recommended action.
        
        Args:
            recommendation (dict): The recommendation from the AI model.
            
        Returns:
            bool: True if the action was executed successfully, False otherwise.
        """
        action = recommendation.get('action')
        
        if action == 'none':
            print(f"No action needed: {recommendation.get('reason')}")
            return True
        
        asset = recommendation.get('asset')
        amount = recommendation.get('amount')
        
        if not asset or amount is None:
            print("Missing asset or amount in recommendation")
            return False
        
        try:
            # Convert the asset symbol to address
            # This would require a mapping of symbols to addresses
            # For simplicity, we're assuming the asset is already an address
            asset_address = asset
            
            # Convert the amount to Wei
            amount_wei = int(amount * 1e18)
            
            if action == 'add_collateral':
                # Deposit more collateral
                tx_hash = self.aave_manager.deposit(asset_address, amount_wei)
                print(f"Added {amount} {asset} as collateral. Transaction hash: {tx_hash}")
                return True
            
            elif action == 'repay_debt':
                # Repay some debt
                # Assuming variable interest rate (2)
                tx_hash = self.aave_manager.repay(asset_address, amount_wei, 2)
                print(f"Repaid {amount} {asset} of debt. Transaction hash: {tx_hash}")
                return True
            
            elif action == 'withdraw_collateral':
                # Withdraw some collateral
                tx_hash = self.aave_manager.withdraw(asset_address, amount_wei)
                print(f"Withdrew {amount} {asset} of collateral. Transaction hash: {tx_hash}")
                return True
            
            elif action == 'borrow_more':
                # Borrow more
                # Assuming variable interest rate (2)
                tx_hash = self.aave_manager.borrow(asset_address, amount_wei, 2)
                print(f"Borrowed {amount} {asset}. Transaction hash: {tx_hash}")
                return True
            
            else:
                print(f"Unknown action: {action}")
                return False
        
        except Exception as e:
            print(f"Error executing recommendation: {e}")
            return False
