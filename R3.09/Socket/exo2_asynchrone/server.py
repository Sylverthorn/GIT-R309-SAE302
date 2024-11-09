import socket
import threading

class Server:
    def __init__(self, port, hosts='0.0.0.0'):
        self.port = port
        self.hosts = hosts
        self.server_socket = socket.socket()
        self.connection = None
        self.reply = "reply Hello, World!"
        

    def __connect(self):
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(1)
        print("Server connecté sur le port: " + str(self.port))

        while True:
            self.connection, address = self.server_socket.accept()
            print("Connexion client : " + str(address))

    def __send_message(self, message=None):
        if message is None:
            message = self.reply
        try:
            self.connection.send(message.encode())
            print(self.connection)
        except (ConnectionAbortedError, BrokenPipeError):
            print("Client déconnecté.")

    def __recois(self):
        while True:
            try:
                message = self.connection.recv(1024).decode()
                print("Message du client: " + message)
                if message :
                    threading.Thread(target=self.__send_message).start()

                if message.lower() == "arret":
                    print("Déconnexion...")
                    self.connection.close()
                    self.server_socket.close()
                    
                    break
                    
            except ConnectionAbortedError:
                print("Client déconnecté.")
                break

    def start(self):
        self.__connect()


        receive_thread = threading.Thread(target=self.__recois)
        receive_thread.start()
        
        receive_thread.join()
        
        

if __name__ == "__main__":
    server = Server(12345)
    server.start()
