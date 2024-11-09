import socket
import threading

class Client():
    def __init__(self,port, host = '127.0.0.1'):
        self.port = port
        self.host = host
        self.client_socket = socket.socket()
        self.boucle = True

    def __cennect(self):
        try:
            self.client_socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            print("Connection refused. Server is not running.")
            try:
                print('')
                self.__cennect()

            except KeyboardInterrupt:
                print("Arret du client ...")
                exit()




    def __send_message(self):
        while self.boucle:
            
    
            message = input("Enter message: ")
            self.client_socket.send(message.encode())

        
            if message.lower() == "bye":
                print("Deconnexion du client...")
                self.client_socket.close()
                self.boucle = False


            elif message.lower() == "arret":
                print("Client and server are shutting down...")
                self.client_socket.close()
                self.boucle = False
            


    def __recois(self):
        while self.boucle:
            try:
                reply = self.client_socket.recv(1024).decode()
                print("Server reply:", reply)
            except ConnectionAbortedError:
                break
            
    def start(self):
        self.__cennect()

        send_thread = threading.Thread(target=self.__send_message)
        receive_thread = threading.Thread(target=self.__recois)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()




if __name__ == "__main__":
    client = Client(12345)
    client.start()