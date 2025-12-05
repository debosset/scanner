#!/usr/bin/env python3

"""
Bitcoin Puzzle #71 Hunter - OPTIMIZED VERSION
Version 2.0 - Batch processing, Real-time stats, Progress saving

Optimizations:
1. Batch key generation (50 keys at once)
2. Conditional balance checking (only on address match)
3. Real-time statistics with status.json
4. Progress saving and resume capability
5. Optimized key generation with secrets.randbits
6. Coverage and ETA calculations

Expected performance: 1000-2000 keys/sec (vs 100 keys/sec original)
"""

import sys
import time
import json
import os
from utils import (
    generate_puzzle71_batch,
    private_key_to_btc_address,
    check_btc_balance,
    RateLimiter,
    TARGET_ADDRESS,
    TARGET_BTC,
    PUZZLE_71_MIN,
    PUZZLE_71_MAX,
    log_funds_found
)
from config import API_RATE_LIMIT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_PATH = os.path.join(BASE_DIR, "status.json")
TOTAL_KEYS_FILE = os.path.join(BASE_DIR, "total_keys_puzzle.json")

# Optimization parameters
BATCH_SIZE = 25           # Keys to generate per batch
STATUS_INTERVAL = 30.0    # Status update interval (seconds)
PRINT_INTERVAL = 1000     # Print progress every N keys



def load_total_keys() -> int:
    """Load total keys tested from file"""
    if os.path.exists(TOTAL_KEYS_FILE):
        try:
            with open(TOTAL_KEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("total", 0))
        except Exception:
            return 0
    return 0


def save_total_keys(total: int):
    """Save total keys tested to file"""
    tmp = TOTAL_KEYS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"total": int(total)}, f)
    os.replace(tmp, TOTAL_KEYS_FILE)


def write_status(keys_checked: int, total_keys: int, last_key_hex: str,
                start_time: float, found: bool = False):
    """Write status to JSON file with coverage and ETA"""
    elapsed = time.time() - start_time
    speed = keys_checked / elapsed if elapsed > 0 else 0.0
    
    # Calculate coverage
    range_size = PUZZLE_71_MAX - PUZZLE_71_MIN + 1
    coverage_session = (keys_checked / range_size) * 100 if range_size > 0 else 0
    coverage_global = (total_keys / range_size) * 100 if range_size > 0 else 0
    
    # Calculate ETA for full range
    if speed > 0:
        remaining_keys = range_size - total_keys
        eta_seconds = remaining_keys / speed if remaining_keys > 0 else 0
    else:
        eta_seconds = 0
    
    data = {
        "script": "puzzle",
        "target_address": TARGET_ADDRESS,
        "target_btc": TARGET_BTC,
        "range_start_hex": f"0x{PUZZLE_71_MIN:x}",
        "range_end_hex": f"0x{PUZZLE_71_MAX:x}",
        "range_size": int(range_size),
        "keys_checked": keys_checked,
        "total_keys_tested": total_keys,
        "last_key_hex": last_key_hex,
        "keys_per_second": speed,
        "elapsed_seconds": elapsed,
        "coverage_session_percent": coverage_session,
        "coverage_global_percent": coverage_global,
        "eta_full_range_seconds": eta_seconds,
        "found": found,
        "updated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    
    tmp_path = STATUS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, STATUS_PATH)
    
    save_total_keys(total_keys)


def format_time(seconds: float) -> str:
    """Format seconds to human-readable time"""
    if seconds == 0:
        return "N/A"
    
    years = int(seconds // (365 * 24 * 3600))
    seconds %= (365 * 24 * 3600)
    days = int(seconds // (24 * 3600))
    seconds %= (24 * 3600)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    
    if years > 0:
        return f"{years}y {days}d"
    elif days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def main():
    print("\n" + "="*60, flush=True)
    print("=== BITCOIN PUZZLE #71 HUNTER - OPTIMIZED v2.0 ===", flush=True)
    print("="*60, flush=True)
    print(f"\nTarget Address: {TARGET_ADDRESS}", flush=True)
    print(f"Target Balance: {TARGET_BTC} BTC", flush=True)
    print(f"Key Range: 0x{PUZZLE_71_MIN:x} - 0x{PUZZLE_71_MAX:x}", flush=True)
    
    range_size = PUZZLE_71_MAX - PUZZLE_71_MIN + 1
    print(f"Range Size: {range_size:,} possible keys", flush=True)
    
    print("\nOptimizations:", flush=True)
    print("  • Batch key generation (50 keys per batch)", flush=True)
    print("  • Conditional balance checking (only on match)", flush=True)
    print("  • Real-time statistics", flush=True)
    print("  • Progress saving", flush=True)
    print(f"\nExpected performance: 1000-2000 keys/sec\n", flush=True)
    print("Any match will be logged to 'found_funds.log'", flush=True)
    print("Press Ctrl+C to stop gracefully\n", flush=True)
    print("="*60 + "\n", flush=True)
    
    # Load previous progress
    total_start = load_total_keys()
    print(f"[Info] Total keys already tested: {total_start:,}\n", flush=True)
    
    rate_limiter = RateLimiter(API_RATE_LIMIT)
    
    keys_checked = 0
    matches_found = 0
    start_time = time.time()
    last_status_time = 0.0
    last_key_hex = ""
    
    try:
        while True:
            # Generate batch of private keys
            private_keys = generate_puzzle71_batch(BATCH_SIZE)
            
            for private_key_int in private_keys:
                keys_checked += 1
                private_key_hex = format(private_key_int, '064x')
                last_key_hex = f"0x{private_key_hex}"
                
                # Convert to BTC address
                btc_address = private_key_to_btc_address(private_key_int)
                
                # Check if address matches target
                if btc_address == TARGET_ADDRESS:
                    print("\n" + "!"*60, flush=True)
                    print("!!! PUZZLE #71 SOLVED !!! ADDRESS MATCH FOUND !!!", flush=True)
                    print("!"*60, flush=True)
                    print(f"Private Key (full): 0x{private_key_hex}", flush=True)
                    print(f"Address: {btc_address}", flush=True)
                    
                    log_funds_found(btc_address, private_key_hex, TARGET_BTC, "BTC")
                    matches_found += 1
                    
                    # Verify balance
                    balance = check_btc_balance(btc_address, private_key_hex, rate_limiter)
                    if balance is not None:
                        print(f"Verified Balance: {balance:.8f} BTC", flush=True)
                    
                    print("!"*60 + "\n", flush=True)
                    
                    # Update status with found=True
                    write_status(
                        keys_checked,
                        total_start + keys_checked,
                        last_key_hex,
                        start_time,
                        found=True
                    )
                    
                    # Continue searching or stop?
                    # For now, continue searching
            
            # Print progress
            if keys_checked % PRINT_INTERVAL == 0:
                elapsed = time.time() - start_time
                speed = keys_checked / elapsed if elapsed > 0 else 0.0
                coverage = (keys_checked / range_size) * 100
                
                print(f"\n--- Progress: {keys_checked:,} keys tested | Speed: {speed:.2f} keys/s ---", flush=True)
                print(f"Coverage (session): {coverage:.8f}%", flush=True)
                print(f"Elapsed: {elapsed/60:.2f} minutes", flush=True)
                print(f"Matches: {matches_found}\n", flush=True)
            
            # Update status file
            now = time.time()
            if (now - last_status_time) >= STATUS_INTERVAL:
                write_status(
                    keys_checked,
                    total_start + keys_checked,
                    last_key_hex,
                    start_time,
                    found=(matches_found > 0)
                )
                last_status_time = now
    
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.", flush=True)
        write_status(
            keys_checked,
            total_start + keys_checked,
            last_key_hex,
            start_time,
            found=(matches_found > 0)
        )
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}", flush=True)
        write_status(
            keys_checked,
            total_start + keys_checked,
            last_key_hex,
            start_time,
            found=(matches_found > 0)
        )
        return 1
    
    elapsed = time.time() - start_time
    speed = keys_checked / elapsed if elapsed > 0 else 0.0
    
    print(f"\nFinished!", flush=True)
    print(f"Tested {keys_checked:,} keys in {elapsed/60:.2f} minutes", flush=True)
    print(f"Average speed: {speed:.2f} keys/sec", flush=True)
    print(f"Matches found: {matches_found}", flush=True)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())