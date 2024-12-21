import psutil
import time
import os
import threading

def stress_cpu():
    """Fonction qui stresse le CPU en effectuant des calculs intensifs."""
    while True:
        _ = sum(i * i for i in range(10_000))  # Charge CPU artificielle

def monitor_cpu():
    """Surveille l'utilisation du CPU et arrête le script si elle dépasse 10%."""
    process = psutil.Process(os.getpid())  # Récupère le processus actuel
    while True:
        cpu_usage = process.cpu_percent(interval=1) / psutil.cpu_count()  # Utilisation CPU par cœur
        print(f"Utilisation CPU : {cpu_usage:.2f}%")
        
        if cpu_usage > 10:  # Seuil d'utilisation
            print("STOP : Utilisation du processeur trop élevée !")
            os._exit(0)  # Termine immédiatement le script
        
        time.sleep(1)  # Pause pour éviter un monitoring constant

if __name__ == "__main__":
    # Lancer le stress du CPU dans un thread séparé
    stress_thread = threading.Thread(target=stress_cpu, daemon=True)
    stress_thread.start()

    # Lancer la surveillance du CPU
    monitor_cpu()
