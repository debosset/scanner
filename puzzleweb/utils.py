import time
import requests
import secrets
import hashlib
from typing import Optional
from datetime import datetime
from threading import Lock

# Bitcoin Puzzle #71 Configuration
PUZZLE_71_MIN = 0x400000000000000000
PUZZLE_71_MAX = 0x7fffffffffffffffff
TARGET_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
TARGET_BTC = 7.10020628


class RateLimiter:
    """Token bucket rate limiter - thread-safe"""
    
    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self.tokens = 1.0
        self.last_call = 0
        self.total_calls = 0
        self.lock = Lock()
        from config import MAX_API_CALLS
        self.max_calls = MAX_API_CALLS
    
    def wait(self):
        """Wait for rate limit and check total calls"""
        with self.lock:
            if self.total_calls >= self.max_calls:
                raise Exception(f"Maximum API calls limit ({self.max_calls}) reached")
            
            now = time.time()
            time_passed = now - self.last_call
            if time_passed < self.min_interval:
                time.sleep(self.min_interval - time_passed)
            
            self.last_call = time.time()
            self.total_calls += 1


def log_funds_found(address: str, private_key: str, balance: float, currency: str = "BTC"):
    """Log when funds are found in an address"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n{'='*60}\n"
    log_entry += f"!!! PUZZLE #71 SOLVED !!!\n"
    log_entry += f"{'='*60}\n"
    log_entry += f"[{timestamp}] Found {balance:.8f} {currency}\n"
    log_entry += f"Address: {address}\n"
    log_entry += f"Private Key (HEX): {private_key}\n"
    log_entry += f"{'='*60}\n"
    
    with open("found_funds.log", "a") as log_file:
        log_file.write(log_entry)
    
    print(log_entry, flush=True)


def generate_puzzle71_private_key() -> int:
    """Generate a random private key within Bitcoin Puzzle #71 range - OPTIMIZED"""
    # Use secrets.randbits for cryptographically secure random generation
    range_size = PUZZLE_71_MAX - PUZZLE_71_MIN + 1
    range_bits = range_size.bit_length()
    
    while True:
        random_value = secrets.randbits(range_bits)
        if random_value < range_size:
            return PUZZLE_71_MIN + random_value


def generate_puzzle71_batch(batch_size: int) -> list:
    """Generate a batch of private keys - OPTIMIZED"""
    return [generate_puzzle71_private_key() for _ in range(batch_size)]


def private_key_to_btc_address(private_key_int: int) -> str:
    """Convert a private key integer to Bitcoin address (compressed P2PKH) - OPTIMIZED"""
    try:
        from ecdsa import SECP256k1, SigningKey
        import hashlib
        
        private_key_bytes = private_key_int.to_bytes(32, byteorder='big')
        
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Compressed public key
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        compressed_pubkey = prefix + x.to_bytes(32, byteorder='big')
        
        # Hash160
        sha256_hash = hashlib.sha256(compressed_pubkey).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        pubkey_hash = ripemd160.digest()
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + pubkey_hash
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum
        
        # Base58 encode
        address = base58_encode(address_bytes)
        
        return address
        
    except Exception as e:
        print(f"Error converting private key to address: {str(e)}", flush=True)
        raise


def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58 (Bitcoin style)"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    num = int.from_bytes(data, 'big')
    
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result
    
    # Handle leading zeros
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break
    
    return result


def check_btc_balance(address: str, private_key_hex: str, rate_limiter: RateLimiter) -> Optional[float]:
    """Check BTC balance using Blockchain.info API and log if funds are found"""
    from config import BLOCKCHAIN_API_ENDPOINT, MAX_RETRIES, RETRY_DELAY
    
    for retry in range(MAX_RETRIES):
        try:
            rate_limiter.wait()
            url = f"{BLOCKCHAIN_API_ENDPOINT}?active={address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 429:
                if retry < MAX_RETRIES - 1:
                    print(f"\nBTC API rate limit, waiting {RETRY_DELAY} seconds...", flush=True)
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    return None
            
            response.raise_for_status()
            data = response.json()
            
            if address in data:
                balance_satoshi = data[address]['final_balance']
                balance_btc = balance_satoshi / 100000000
                
                if balance_btc > 0:
                    log_funds_found(address, private_key_hex, balance_btc, "BTC")
                
                return balance_btc
            
            return 0.0
            
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"\nBTC balance check error: {str(e)}", flush=True)
    
    return None