# Kamisado AI – AdvancedPython2BA-Labo1

> Binôme : **[Matricule 1]** – **[Matricule 2]**

---

## Stratégie

Notre IA utilise l'algorithme **Minimax avec élagage Alpha-Beta**.

### Minimax
Minimax est un algorithme d'exploration d'arbre de jeu à deux joueurs à somme nulle.
À chaque nœud de l'arbre :
- Si c'est notre tour (**maximisant**) → on choisit le coup qui maximise le score.
- Si c'est le tour de l'adversaire (**minimisant**) → on suppose qu'il choisit le coup qui minimise notre score.

### Élagage Alpha-Beta
L'élagage Alpha-Beta évite d'explorer des branches inutiles sans modifier le résultat final de Minimax. Cela permet d'augmenter la profondeur de recherche pour la même quantité de calcul.

### Fonction d'évaluation heuristique
Lorsque la profondeur maximale est atteinte, on évalue le plateau avec une heuristique composée de :

| Composante | Description |
|---|---|
| **Avancement** | Récompense les jetons proches de la rangée adverse (×10) |
| **Centralité** | Préfère les colonnes centrales, plus flexibles (×2) |
| **Pénalité adversaire** | Soustrait le score d'avancement de l'adversaire |

### Paramètres
- **Profondeur de recherche** : 3 (modifiable via `MINIMAX_DEPTH` dans `strategy.py`)
- Une profondeur plus élevée donne une IA plus forte mais plus lente.

---

## Structure du projet

```
.
├── client.py          # Client principal – connexion serveur et boucle de jeu
├── strategy.py        # Logique IA : Minimax, Alpha-Beta, heuristique
├── tests/
│   └── test_strategy.py   # Tests unitaires (>80% de couverture)
└── README.md
```

---

## Bibliothèques utilisées

| Bibliothèque | Usage | Installation |
|---|---|---|
| `requests` | Communication HTTP avec le serveur de parties | `pip install requests` |
| `pytest` | Framework de tests unitaires | `pip install pytest` |
| `pytest-cov` | Mesure de la couverture des tests | `pip install pytest-cov` |
| `copy` | Deep copy du plateau (stdlib) | – |

---

## Lancer le client

```bash
python client.py <url_serveur> <nom_joueur>

# Exemple :
python client.py http://192.168.1.42:5000 MinimaxAI
```

---

## Lancer les tests

```bash
# Tests simples
pytest tests/

# Avec rapport de couverture
pytest tests/ --cov=strategy --cov-report=term-missing
```

---

## Résultats attendus

- ✅ Zéro *Bad Move* (validation stricte des coups)
- ✅ Meilleure que l'IA aléatoire (*Random*)
- ✅ Couverture de tests > 80 %
