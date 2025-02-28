import time
import argparse
import logging
from src.aave_manager import AaveManager
from src.chainlink_oracle import ChainlinkOracle
from src.ai_position_manager import AIPositionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("position_manager.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("position_manager")

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="AI-powered DeFi position manager")
    
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Monitoring interval in seconds (default: 300)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no transactions will be executed)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    return parser.parse_args()

def main():
    """
    Main function to run the position manager.
    """
    args = parse_arguments()
    
    # Set log level
    logger.setLevel(getattr(logging, args.log_level))
    
    logger.info("Starting AI-powered DeFi position manager")
    
    try:
        # Initialize components
        logger.info("Initializing Aave manager")
        aave_manager = AaveManager()
        
        logger.info("Initializing Chainlink oracle")
        chainlink_oracle = ChainlinkOracle()
        
        logger.info("Initializing AI position manager")
        ai_manager = AIPositionManager(aave_manager, chainlink_oracle)
        
        # Main monitoring loop
        logger.info(f"Starting monitoring loop with interval of {args.interval} seconds")
        
        while True:
            try:
                # Check if position is safe
                health_factor = aave_manager.get_health_factor()
                logger.info(f"Current health factor: {health_factor}")
                
                is_safe = aave_manager.is_position_safe()
                logger.info(f"Position safe: {is_safe}")
                
                # Get market data
                prices = chainlink_oracle.get_all_prices()
                logger.info(f"Current prices: {prices}")
                
                # Get AI recommendation
                logger.info("Getting AI recommendation")
                recommendation = ai_manager.get_ai_recommendation()
                logger.info(f"AI recommendation: {recommendation}")
                
                # Execute recommendation if not in dry-run mode
                if not args.dry_run and recommendation['action'] != 'none':
                    logger.info(f"Executing recommendation: {recommendation['action']}")
                    success = ai_manager.execute_recommendation(recommendation)
                    logger.info(f"Execution {'successful' if success else 'failed'}")
                elif args.dry_run and recommendation['action'] != 'none':
                    logger.info(f"Dry run mode: would execute {recommendation['action']}")
                
                # Wait for the next interval
                logger.info(f"Waiting for {args.interval} seconds")
                time.sleep(args.interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                logger.info(f"Waiting for {args.interval} seconds before retrying")
                time.sleep(args.interval)
    
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
