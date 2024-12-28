# Documentation de Développement

Ce projet met en œuvre un système client-serveur avec des interfaces graphiques pour gérer les interactions entre clients, serveurs et serveurs secondaires.

---

## Sommaire

1. [Client](#client)
2. [Interface Client](#interface-client)
3. [Interface Server](#interface-server)
4. [Server](#server)
5. [Server Second](#server-second)

---

## Client

### Classe Client

#### Attributs
- **`port`** : Le port sur lequel le client se connecte au serveur.
- **`host`** : L'adresse IP du serveur.
- **`client_socket`** : Le socket utilisé pour la communication avec le serveur.
- **`state`** : L'état actuel du client (`shutdown`, `in progress`, `running`).
- **`resultat`** : Stocke le résultat reçu du serveur.

#### Méthodes
- **`__init__(self, port='2300', host='127.0.0.1')`** : Constructeur. Initialise les attributs et configure le socket.
- **`connect(self)`** : Établit une connexion avec le serveur, avec tentative de reconnexion jusqu'à 5 fois.
- **`__reconnexion(self)`** : Ferme le socket actuel et tente une reconnexion.
- **`__envoi_message(self, message)`** : Envoie un message au serveur (chaîne ou bytes).
- **`__recois_message(self)`** : Boucle de réception des messages du serveur.
- **`envoi(self, message)`** : Démarre un thread pour envoyer un message au serveur.
- **`recois(self)`** : Démarre un thread pour recevoir des messages.
- **`arret(self)`** : Arrête le client en fermant le socket et en changeant l'état à `shutdown`.
- **`quitter(self)`** : Arrête le client proprement et termine le programme.

---

## Interface Client

### Classe MainWindow

#### Attributs
- **`nom_fichier`** : Nom du fichier à envoyer.
- **`client`** : Instance de la classe `Client`.

#### Méthodes
- **`__init__(self)`** : Constructeur. Initialise les widgets et les connexions.
- **`ferme(self)`** : Arrête le client et quitte l'application.
- **`demarrage(self)`** : Démarre ou arrête le client en fonction de son état.
- **`envoyer_message(self)`** : Envoie un message ou un fichier au serveur.
- **`thread_demarrage(self)`** : Démarre un thread pour la connexion au serveur.
- **`monitor_state(self)`** : Surveille l'état du client et met à jour l'interface.
- **`monitor_results(self)`** : Surveille les résultats reçus du serveur et les affiche.
- **`choisir_fichier(self)`** : Ouvre une boîte de dialogue pour choisir un fichier.
- **`log_message(self, message)`** : Affiche un message dans la zone de logs.
- **`update_results(self, result)`** : Affiche les résultats reçus du serveur.
- **`closeEvent(self, event)`** : Gère la fermeture de la fenêtre.

---

## Interface Server

### Classe ServerGUI

#### Attributs
- **`server`** : Instance de la classe `Server`.
- **`local_mode`** : Indique si le mode local est activé.

#### Méthodes
- **`__init__(self)`** : Constructeur. Initialise les widgets et les connexions.
- **`init_config_fields(self, layout)`** : Initialise les champs de configuration.
- **`toggle_local_mode(self)`** : Active ou désactive le mode local.
- **`toggle_server(self)`** : Démarre ou arrête le serveur.
- **`start_server(self)`** : Démarre le serveur.
- **`stop_server(self)`** : Arrête le serveur.
- **`close_application(self)`** : Ferme l'application.
- **`update_server_list(self)`** : Met à jour la liste des serveurs secondaires.

---

## Server

### Classe Server

#### Attributs
- **`hosts`** : Adresse IP du serveur.
- **`ip`** : Adresse IP du serveur maître.
- **`port_serv`** : Port du serveur secondaire.
- **`server_socket`** : Socket du serveur secondaire.
- **`port_client`** : Port du client.
- **`client_socket`** : Socket du client.
- **`liste_clients`** : Liste des clients connectés.
- **`serveurs_secondaires`** : Liste des serveurs secondaires.
- **`max_taches`** : Nombre maximum de tâches.
- **`cpu_max`** : Utilisation maximale du CPU.
- **`nb_server`** : Nombre de serveurs secondaires.
- **`local`** : Indique si le mode local est activé.

#### Méthodes
- **`__init__(self, ip, max_taches, cpu=10, port_client=4200, port_serv=5200, local=True, nb_server=2, hosts='0.0.0.0')`** : Constructeur. Initialise les attributs et configure les sockets.
- **`start_client_socket(self, host, port_client)`** : Démarre le socket client.
- **`start_server_socket(self, host, port_serv)`** : Démarre le socket serveur.
- **`accept_client(self)`** : Accepte les connexions des clients.
- **`accept_server(self)`** : Accepte les connexions des serveurs secondaires.
- **`__envoi_message(self, message, client=None)`** : Envoie un message au client ou au serveur secondaire.
- **`__recois(self, client=None, numero_client=None)`** : Boucle de réception des messages des clients.
- **`toujours_là(self, client, numero_client)`** : Vérifie si le client est toujours connecté.
- **`initialisation_serveur_secondaire(self)`** : Initialise les serveurs secondaires.
- **`load_balancing(self, task, client)`** : Répartit les tâches entre les serveurs secondaires.
- **`creation_servsecond(self)`** : Crée un nouveau serveur secondaire.
- **`envoi_tache(self, task, numero_serv, available_server, client)`** : Envoie une tâche à un serveur secondaire.
- **`stop(self)`** : Arrête le serveur et les serveurs secondaires.
- **`start(self)`** : Démarre le serveur et accepte les connexions.

---

## Server Second

### Classe Server

#### Attributs
- **`master_host`** : Adresse IP du serveur maître.
- **`master_port`** : Port du serveur maître.
- **`server_socket`** : Socket du serveur secondaire.
- **`nb_taches`** : Nombre maximum de tâches.
- **`cpu_max`** : Utilisation maximale du CPU.
- **`usage_cpu`** : Utilisation actuelle du CPU.
- **`file_attente`** : File d'attente des tâches.

#### Méthodes
- **`__init__(self, master_host, master_port, nb_taches, cpu=2)`** : Constructeur. Initialise les attributs et configure le socket.
- **`__connect(self)`** : Connecte le serveur secondaire au serveur maître.
- **`register_to_master(self)`** : Enregistre le serveur secondaire auprès du maître.
- **`__envoi_message(self, message)`** : Envoie un message au serveur maître.
- **`__recois(self)`** : Boucle de réception des messages du maître.
- **`file_execution(self)`** : Exécute les tâches en attente.
- **`fichier(self, message)`** : Crée un fichier à partir du message reçu.
- **`utilisation_cpu(self, process)`** : Surveille l'utilisation du CPU.
- **`python(self, fichier)`** : Exécute un script Python.
- **`c(self, fichier)`** : Compile et exécute un programme C.
- **`java(self, fichier)`** : Compile et exécute un programme Java.
- **`cpp(self, fichier)`** : Compile et exécute un programme C++.
- **`execute_script(self, fichier)`** : Exécute un script selon son type.
- **`start(self)`** : Démarre le serveur secondaire et se connecte au serveur maître.

---
