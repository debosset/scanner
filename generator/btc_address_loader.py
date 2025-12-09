#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitcoin Address List Loader
Télécharge et charge la liste d'adresses Bitcoin en mémoire
"""

import os
import gzip
import requests
from typing import Set
import time

BTC_ADDRESSES_URL = "http://addresses.loyce.club/Bitcoin_addresses_LATEST.txt.gz"
CACHE_FILE = "bitcoin_addresses.txt.gz"
ADDRESSES_SET_CACHE = "btc_addresses.cache"


def download_btc_addresses(force_download: bool = False) -> str:
    """
    Télécharge le fichier d'adresses Bitcoin
    
    Args:
        force_download: Force le téléchargement même si le fichier existe
        
    Returns:
        Chemin vers le fichier téléchargé
    """
    if os.path.exists(CACHE_FILE) and not force_download:
        print(f"[Info] Fichier {CACHE_FILE} déjà présent, téléchargement ignoré.")
        return CACHE_FILE
    
    print(f"[Info] Téléchargement de {BTC_ADDRESSES_URL}...")
    print("[Info] Cela peut prendre plusieurs minutes...")
    
    start_time = time.time()
    
    try:
        response = requests.get(BTC_ADDRESSES_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(CACHE_FILE, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r[Info] Téléchargement: {progress:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end='', flush=True)
        
        elapsed = time.time() - start_time
        print(f"\n[Info] Téléchargement terminé en {elapsed:.1f} secondes")
        print(f"[Info] Fichier sauvegardé: {CACHE_FILE}")
        
        return CACHE_FILE
        
    except Exception as e:
        print(f"\n[Erreur] Échec du téléchargement: {e}")
        raise


def load_btc_addresses_to_set(gz_file: str) -> Set[str]:
    """
    Charge les adresses Bitcoin depuis le fichier .gz dans un set Python
    
    Args:
        gz_file: Chemin vers le fichier .gz
        
    Returns:
        Set contenant toutes les adresses Bitcoin
    """
    print(f"\n[Info] Chargement des adresses Bitcoin en mémoire...")
    print("[Info] Cela peut prendre 1-3 minutes selon la taille du fichier...")
    
    start_time = time.time()
    addresses = set()
    
    try:
        with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                address = line.strip()
                if address:  # Ignore les lignes vides
                    addresses.add(address)
                
                # Afficher la progression tous les 1 million d'adresses
                if i % 1_000_000 == 0:
                    print(f"\r[Info] Chargé: {i:,} adresses ({len(addresses):,} uniques)", end='', flush=True)
        
        elapsed = time.time() - start_time
        print(f"\n[Info] Chargement terminé en {elapsed:.1f} secondes")
        print(f"[Info] Total d'adresses uniques: {len(addresses):,}")
        print(f"[Info] Mémoire estimée: ~{len(addresses) * 50 / 1024 / 1024:.1f} MB")
        
        return addresses
        
    except Exception as e:
        print(f"\n[Erreur] Échec du chargement: {e}")
        raise


def initialize_btc_address_set(force_download: bool = False) -> Set[str]:
    """
    Initialise le set d'adresses Bitcoin (télécharge si nécessaire)
    
    Args:
        force_download: Force le téléchargement même si le fichier existe
        
    Returns:
        Set contenant toutes les adresses Bitcoin
    """
    print("\n" + "="*60)
    print("=== Initialisation de la liste d'adresses Bitcoin ===")
    print("="*60 + "\n")
    
    # Télécharger le fichier si nécessaire
    gz_file = download_btc_addresses(force_download)
    
    # Charger en mémoire
    addresses = load_btc_addresses_to_set(gz_file)
    
    print("\n[Info] ✓ Initialisation terminée avec succès!")
    print(f"[Info] Le set contient {len(addresses):,} adresses Bitcoin\n")
    
    return addresses


if __name__ == "__main__":
    # Test du chargement
    btc_addresses = initialize_btc_address_set()
    
    # Test de recherche
    print("\n=== Test de recherche ===")
    test_addr = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Adresse Genesis de Satoshi
    
    start = time.time()
    is_known = test_addr in btc_addresses
    elapsed = time.time() - start
    
    print(f"Adresse testée: {test_addr}")
    print(f"Résultat: {'TROUVÉE' if is_known else 'NON TROUVÉE'}")
    print(f"Temps de recherche: {elapsed*1000:.3f} ms")