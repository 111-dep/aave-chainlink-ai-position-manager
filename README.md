# AI-Powered DeFi Position Manager

This project demonstrates an AI-powered DeFi position manager that uses Aave for staking and Chainlink oracles to provide real-time data to an AI model. The AI model analyzes the data and makes recommendations to manage positions and prevent liquidation.

## Features

- Integration with Aave protocol for lending and borrowing operations
- Real-time price data from Chainlink oracles
- AI-powered position management recommendations
- Automatic execution of recommended actions
- Configurable monitoring interval and safety parameters

## Architecture

The project is structured as follows:

- `src/`: Core application code
  - `aave_manager.py`: Handles interactions with Aave protocol
  - `chainlink_oracle.py`: Fetches price data from Chainlink oracles
  - `ai_position_manager.py`: Uses AI to analyze data and make recommendations
  - `main.py`: Main application entry point
- `config/`: Configuration files
  - `config.py`: Central configuration module
- `utils/`: Utility functions
  - `web3_utils.py`: Web3 connection and transaction utilities
- `scripts/`: Helper scripts
  - `run_position_manager.py`: Script to run the position manager
- `tests/`: Test files (to be implemented)

## Prerequisites

- Python 3.8 or higher
- Ethereum wallet with funds
- Aave positions (collateral and/or debt)
- OpenAI API key (or other AI provider)
- Infura API key (or other Ethereum provider)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aave-chainlink-ai-position-manager.git
   cd aave-chainlink-ai-position-manager
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the `.env.example` file:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your configuration:
   - Add your wallet address and private key
   - Add your OpenAI API key
   - Configure Aave and Chainlink addresses
   - Set your preferred parameters

## Usage

Run the position manager:

```
python scripts/run_position_manager.py
```

### Command Line Options

- `--interval`: Monitoring interval in seconds (default: 300)
- `--dry-run`: Run in dry-run mode (no transactions will be executed)
- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Example:

```
python scripts/run_position_manager.py --interval 60 --dry-run --log-level DEBUG
```

## How It Works

1. The application connects to the Aave protocol and Chainlink oracles
2. It periodically collects data about your position and market conditions
3. The AI model analyzes the data and makes recommendations
4. If the position is at risk, the application can automatically:
   - Add more collateral
   - Repay some debt
   - Adjust positions to maintain a safe health factor

## Security Considerations

- Store your private key securely
- Use a dedicated wallet for this application
- Start with small positions and test thoroughly
- Use the `--dry-run` option to test without executing transactions

## Customization

You can customize the behavior of the position manager by modifying the parameters in the `.env` file:

- `LIQUIDATION_THRESHOLD_BUFFER`: Buffer above the liquidation threshold
- `HEALTH_FACTOR_MIN`: Minimum acceptable health factor
- `AI_MODEL`: The AI model to use for recommendations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided for educational and demonstration purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred by using this software.
