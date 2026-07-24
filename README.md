<<<<<<< HEAD
# CBS — Mini Core Banking System

API REST développée avec Django / Django REST Framework dans le cadre du test technique Backend Django/DRF. Elle couvre la gestion des clients et wallets, les dépôts, les transferts entre wallets, le paiement de factures, ainsi que l'historique et le reporting des transactions.

## Sommaire

- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Modèles de données](#modèles-de-données)
- [Documentation de l'API](#documentation-de-lapi)
- [Modules & endpoints](#modules--endpoints)
- [Tests](#tests)
- [Problèmes connus & recommandations](#problèmes-connus--recommandations)

## Stack technique

- Python 3.11
- Django 5.2
- Django REST Framework
- django-filter
- PostgreSQL (via `psycopg2`)

## Structure du projet

```
CBS/
├── CBS/            # Configuration du projet (settings, urls racine, wsgi/asgi)
├── bank/           # Sujet 1 — Clients & Wallets
├── deposits/       # Sujet 2 — Dépôts
├── transfer/       # Sujet 3 — Transferts entre wallets
├── paiement/       # Sujet 4 — Fournisseurs, factures, paiements
├── historique/     # Sujet 5 — Historique & reporting
└── manage.py
```

Chaque app métier suit la même organisation : `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `migrations/`.

## Prérequis

- Python 3.11 ou supérieur
- PostgreSQL 14 ou supérieur
- `pip` et `venv`

## Installation

### 1. Cloner le projet

```bash
git clone <url_du_repo>
cd CBS
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données PostgreSQL

Créer la base de données :

```sql
CREATE DATABASE cbs_db;
```

Renseigner les identifiants dans `CBS/settings.py` (section `DATABASES`) :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cbs_db',
        'USER': '<votre_utilisateur>',
        'PASSWORD': '<votre_mot_de_passe>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

> ⚠️ Voir la section [Problèmes connus](#problèmes-connus--recommandations) : les identifiants sont actuellement en clair dans `settings.py`.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. (Optionnel) Créer un superutilisateur pour l'admin Django

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'API est accessible sur `http://127.0.0.1:8000/`.

## Modèles de données

| Modèle | App | Champs principaux |
|---|---|---|
| `Client` | bank | `id` (UUID), `name`, `age` (optionnel), `adress`, `phone` |
| `Wallet` | bank | `id`, `client` (FK → Client), `balance` (décimal, défaut 0), `currency` (défaut `fbi`) |
| `Deposit` | deposits | `id`, `wallet` (FK), `amount`, `channel` (`CASH` / `MOBILE_MONEY` / `BANK_TRANSFER`), `created_at` |
| `Transfer` | transfer | `id`, `source_wallet` (FK), `destination_wallet` (FK), `amount`, `created_at` |
| `ServiceProvider` | paiement | `id`, `name`, `category` (`ELECTRICITY` / `WATER` / `INTERNET` / `TV`) |
| `Bill` | paiement | `id`, `provider` (FK), `reference_number`, `amount_due`, `is_paid` |
| `Payment` | paiement | `id`, `wallet` (FK), `bill` (FK), `amount`, `created_at` |

Les opérations financières (dépôt, transfert, paiement) sont exécutées dans des transactions atomiques (`transaction.atomic()`) avec verrouillage de lignes (`select_for_update()`) pour éviter les conditions de course sur les soldes.

## Documentation de l'API

Deux formats sont fournis en complément de ce README :

- **`openapi.yaml`** — spécification OpenAPI 3.0 (Swagger). Importable dans [Swagger Editor](https://editor.swagger.io/), Swagger UI, Postman ou Insomnia pour explorer et tester l'API de façon interactive.
- **`CBS.postman_collection.json`** — collection Postman prête à l'emploi, avec exemples de requêtes/réponses pour chaque endpoint.

Pour importer la collection Postman : *Postman → Import → sélectionner le fichier `CBS.postman_collection.json`*. Une variable de collection `base_url` (défaut `http://127.0.0.1:8000`) est utilisée dans toutes les requêtes.

## Modules & endpoints

### Sujet 1 — Clients & Wallets

Préfixe : `/client wallet/` *(voir remarque ci-dessous sur l'espace dans l'URL)*

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/client wallet/clients/` | Lister les clients (avec leurs wallets) |
| POST | `/client wallet/clients/` | Créer un client |
| GET | `/client wallet/clients/{id}/` | Détail d'un client |
| PUT/PATCH | `/client wallet/clients/{id}/` | Modifier un client |
| DELETE | `/client wallet/clients/{id}/` | Supprimer un client |
| GET | `/client wallet/wallets/` | Lister les wallets |
| POST | `/client wallet/wallets/` | Créer un wallet pour un client |
| GET | `/client wallet/wallets/{id}/` | Détail d'un wallet |
| PUT/PATCH | `/client wallet/wallets/{id}/` | Modifier un wallet |
| DELETE | `/client wallet/wallets/{id}/` | Supprimer un wallet |
| GET | `/client wallet/wallets/{id}/balance/` | Consulter le solde d'un wallet |

### Sujet 2 — Dépôts

Préfixe : `/deposit/`

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/deposit/` | Historique des dépôts. Filtres : `?wallet=`, `?channel=`. Tri : `?ordering=created_at` ou `amount` |
| POST | `/deposit/` | Effectuer un dépôt sur un wallet (crédite automatiquement le solde) |

### Sujet 3 — Transferts

Préfixe : `/transfer/`

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/transfer/` | Historique des transferts. Filtres : `?source_wallet=`, `?destination_wallet=`. Tri : `?ordering=created_at` ou `amount` |
| POST | `/transfer/` | Transférer un montant entre deux wallets. Rejeté si solde insuffisant ou si source = destination |

### Sujet 4 — Paiement de factures

Préfixe : `/paiement/`

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/paiement/providers/` | Lister les fournisseurs de services |
| POST | `/paiement/providers/` | Créer un fournisseur |
| GET | `/paiement/bills/` | Lister les factures. Filtres : `?provider=`, `?is_paid=` |
| POST | `/paiement/bills/` | Créer une facture |
| GET | `/paiement/payments/` | Historique des paiements. Filtres : `?wallet=`, `?bill=`. Tri : `?ordering=created_at` ou `amount` |
| POST | `/paiement/payments/` | Payer une facture depuis un wallet (rejeté si déjà payée ou solde insuffisant) |

### Sujet 5 — Historique & reporting

Préfixe : `/historique/`

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/historique/clients/{client_id}/transactions/` | Toutes les transactions d'un client (dépôts, transferts, paiements). Filtre : `?type=DEPOSIT\|TRANSFER\|PAYMENT` |
| GET | `/historique/clients/{client_id}/transactions/stats/` | Statistiques : total dépôts, total transferts, total paiements, nombre total de transactions |

> ⚠️ Voir [Problèmes connus](#problèmes-connus--recommandations) : ces deux endpoints utilisent actuellement un `client_id` de type entier alors que `Client.id` est un UUID.

## Tests

Aucun test automatisé n'est actuellement implémenté : les fichiers `tests.py` de chaque app sont vides. Le cahier des charges du test technique liste explicitement les tests automatisés comme livrable attendu et comme critère d'évaluation — c'est un point à traiter avant rendu final.

Pistes recommandées pour la suite :
- `bank` : création client/wallet, unicité, sérialisation des wallets imbriqués.
- `deposits` : dépôt valide, montant ≤ 0 rejeté, mise à jour correcte du solde.
- `transfer` : transfert valide, solde insuffisant rejeté, source = destination rejeté, atomicité en cas d'erreur.
- `paiement` : paiement valide, facture déjà payée rejetée, solde insuffisant rejeté, passage de `is_paid` à `True`.
- `historique` : agrégation correcte des montants et du nombre de transactions, filtrage par type.

## Problèmes connus & recommandations

Éléments identifiés en documentant le projet, à corriger avant mise en production ou rendu final :

- **Espace dans l'URL** : le préfixe `/client wallet/` (dans `CBS/urls.py`) contient un espace, encodé en `%20` dans les requêtes. Recommandation : renommer en `/bank/` ou `/clients-wallets/`.
- **Incohérence de type sur `client_id`** : `historique/urls.py` déclare `<int:client_id>` alors que `Client.id` est un `UUIDField`. Ces deux endpoints ne matcheront jamais un identifiant client réel tant que ce n'est pas corrigé en `<uuid:client_id>`.
- **Secrets en clair** : `SECRET_KEY` et les identifiants PostgreSQL sont codés en dur dans `CBS/settings.py`. À déplacer vers des variables d'environnement (ex. `django-environ`, `python-decouple`) et à exclure du contrôle de version.
- **Configuration de production** : `DEBUG = True` et `ALLOWED_HOSTS = []` doivent être ajustés avant tout déploiement.
- **Absence d'authentification** : aucune classe de permission n'est configurée sur les vues ; toutes les APIs sont actuellement accessibles sans authentification, alors que le cahier des charges mentionne la sécurité des API comme critère d'évaluation.
- **Format de devise** : `Wallet.currency` a pour valeur par défaut `"fbi"` (minuscules) — à vérifier/uniformiser selon un format ISO 4217 (ex. `BIF`).
- **Tests automatisés absents** — voir section [Tests](#tests).
=======
# Core-Banking-System
>>>>>>> 3d2f86228e169e6c83fca37248113d45264738bf
