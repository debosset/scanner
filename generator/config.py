import os

# API endpoints
ETHERSCAN_API_ENDPOINT = "https://api.etherscan.io/v2/api"
BLOCKCHAIN_API_ENDPOINT = "https://blockchain.info/balance"  # Bitcoin

# API keys with fallbacks
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "BNIM4UYRSF3QUJ6AS7JITT8KUQIQJ7SA4Z")

# Rate limiting settings (in seconds)
# 2 APIs per address (ETH + BTC)
API_RATE_LIMIT = 0.25  # 0.25 seconds per API call (4 calls/second)
MAX_API_CALLS = 2000000  # Maximum number of API calls allowed (2 per address)

# Number of words in mnemonic
MNEMONIC_WORD_COUNT = 24

# Max retries for API calls
MAX_RETRIES = 3
RETRY_DELAY = 5  # Reduced retry delay to 5 seconds