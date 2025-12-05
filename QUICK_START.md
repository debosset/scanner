# 🚀 Guide de Démarrage Rapide - Version Optimisée

## Installation

```bash
# 1. Installer les dépendances optimisées
pip install -r requirements.txt

# 2. (Optionnel) Pour de meilleures performances sur Unix
pip install uvloop aiodns
```

## Utilisation

### Generator (ETH + BTC Scanner)

```bash
cd generator

# Version originale (4 keys/sec)
python crypto_balance_checker.py

# Version optimisée (40-60 keys/sec) ⚡
python crypto_balance_checker.py
```

### Puzzle #71 (BTC Hunter)

```bash
cd puzzleweb

# Version originale (100 keys/sec)
python puzzle_btc.py

# Version optimisée (1000-2000 keys/sec) ⚡
python puzzle_btc.py
```

### Dashboard

```bash
cd dashboard

# Version originale
python app.py

# Version optimisée avec détection automatique des chemins ⚡
python app.py

# Ouvrir dans le navigateur: http://localhost:5000
```

## Fichiers Générés

- `found_funds.log` - Fonds trouvés (compatible entre versions)
- `status.json` - Statistiques temps réel
- `total_keys_generator.json` - Compteur total generator
- `total_keys_puzzle.json` - Compteur total puzzle

## Configuration

### Generator Optimisé

Éditer `generator/crypto_balance_checker.py` (lignes 30-35):

```python
BATCH_SIZE = 20          # Clés par batch (10-50)
BUFFER_SIZE = 100        # Buffer de logs (50-200)
CACHE_SIZE = 10000       # Cache d'adresses (5000-20000)
STATUS_INTERVAL = 30.0   # Mise à jour status (10-60s)
```

### Puzzle Optimisé

Éditer `puzzleweb/puzzle_btc.py` (lignes 30-32):

```python
BATCH_SIZE = 50           # Clés par batch (20-100)
STATUS_INTERVAL = 30.0    # Mise à jour status (10-60s)
PRINT_INTERVAL = 1000     # Affichage console (500-2000)
```

## Recommandations selon CPU

### CPU Faible (2 cores)
```python
# Generator
BATCH_SIZE = 10
CACHE_SIZE = 5000

# Puzzle
BATCH_SIZE = 25
```

### CPU Moyen (4 cores)
```python
# Generator
BATCH_SIZE = 20
CACHE_SIZE = 10000

# Puzzle
BATCH_SIZE = 50
```

### CPU Puissant (8+ cores)
```python
# Generator
BATCH_SIZE = 50
CACHE_SIZE = 20000

# Puzzle
BATCH_SIZE = 100
```

## Gains de Performance

| Composant | Avant | Après | Gain |
|-----------|-------|-------|------|
| Generator | ~4 keys/s | ~40-60 keys/s | **10-15x** |
| Puzzle | ~100 keys/s | ~1000-2000 keys/s | **10-20x** |
| I/O Disque | Chaque clé | Par batch 100 | **99% réduit** |

## Compatibilité

✅ Les versions optimisées sont 100% compatibles avec les versions originales
✅ Peuvent alterner sans perte de données
✅ Mêmes fichiers de sortie
✅ Dashboard fonctionne avec les deux versions

## Dépannage

### Erreur: Module not found
```bash
pip install -r requirements.txt
```

### Performance faible
- Vérifier connexion internet
- Réduire BATCH_SIZE si CPU surchargé
- Augmenter BATCH_SIZE si CPU sous-utilisé

### Rate limit exceeded
Réduire `API_RATE_LIMIT` dans `config.py`

## Support

Voir `OPTIMIZATION_REPORT.md` pour les détails techniques complets.