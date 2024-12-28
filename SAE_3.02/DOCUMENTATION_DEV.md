# Client Serveur Python

Ce projet implémente un **client** capable de :
- Se connecter à un serveur.
- Envoyer et recevoir des messages.
- Gérer les états de connexion.

Le client est implémenté dans le fichier `client.py`.

---

## Table des Matières
1. [Introduction](#introduction)
2. [Classe Client](#classe-client)
   - [Attributs](#attributs)
   - [Méthodes](#méthodes)
3. [Utilisation](#utilisation)
   - [Exemple de Code](#exemple-de-code)
   - [Instructions](#instructions)
4. [Gestion des Erreurs](#gestion-des-erreurs)

---

## Introduction

Le client implémente une communication via socket avec un serveur, en gérant les reconnections automatiques et divers états (shutdown, in progress, running).

---

## Classe Client

### Attributs
- **`port`** : Le port sur lequel le client se connecte au serveur.
- **`host`** : L'adresse IP du serveur.
- **`client_socket`** : Le socket utilisé pour la communication avec le serveur.
- **`state`** : L'état actuel du client (`shutdown`, `in progress`, `running`).
- **`resultat`** : Stocke le résultat reçu du serveur.

### Méthodes

#### `__init__(self, port='2300', host='127.0.0.1')`
Constructeur de la classe Client.  
- Initialise les attributs et configure le socket.

#### `connect(self)`
- Établit une connexion avec le serveur.
- Tente de se reconnecter jusqu'à **5 fois** en cas d'échec.

#### `__reconnexion(self)`
- Ferme le socket actuel et tente une reconnexion immédiate au serveur.

#### `__envoi_message(self, message)`
- Envoie un message au serveur.  
- Accepte une chaîne de caractères ou des bytes.

#### `__recois_message(self)`
- Boucle de réception des messages du serveur.  
- Gère les différents types de messages (`resultat`, `hello`, `shutdown`).

#### `envoi(self, message)`
- Démarre un thread pour envoyer un message au serveur.

#### `recois(self)`
- Démarre un thread pour recevoir des messages du serveur.

#### `arret(self)`
- Arrête le client en fermant le socket et en changeant l'état à `shutdown`.

#### `quitter(self)`
- Arrête le client proprement et termine le programme.

---

## Utilisation

### Exemple de Code

```python
from client import Client

# Création d'une instance de Client
client = Client(port='2300', host='127.0.0.1')

# Connexion au serveur
client.connect()

# Envoi d'un message
client.envoi("Hello, serveur !")

# Arrêt du client
client.arret()

# Quitter le programme
client.quitter()
    
