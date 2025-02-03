import json
import argparse
import os
import requests

class Entité: 
    def __init__(self, id: int, name: str):
       self.id=id
       self.name=name

    def __repr__(self):
        return f"{self.id}, {self.name}"

class User(Entité):
    def to_dict(self):
        return {"id": self.id, "name": self.name}

class Channel(Entité):
    def to_dict(self):
        return {"id": self.id, "name": self.name}

class Message():
    def __init__(self, id, channel_id, content):
        self.id = id
        self.channel_id = channel_id
        self.content = content

    def to_dict(self):
        return {"id": self.id, "channel": self.channel_id, "content": self.content}


class BaseServer: 

#@abstractmethod
    def get_channels(self):
        pass

    def create_channel(self, name):
        pass
    def delete_channel(self,channel_id):
        pass

    def get_users(self):
        pass

    def create_user(self, name):
        pass

    def ban_user(self, name):
        pass

    def send_message(self, channel_id, content):
        pass

class Server(BaseServer) :
    def __init__(self, file_path):
        self.file_path = file_path
        self.users = []
        self.channels = []
        self.messages = []

    def load(self):
         if not self.file_path:
           raise ValueError("Le chemin du fichier JSON est manquant. Utilisez l'argument --server pour spécifier un fichier.")
         with open(self.file_path, "r") as f:
               server = json.load(f)
               self.users = [User(id=user['id'], name=user['name']) for user in server.get('users', [])]
               self.channels = [Channel(id=channel['id'], name=channel['name']) for channel in server.get('channels', [])]
               self.messages = [Message(id=message['id'], channel_id=message['channel'], content=message['content']) for message in server.get('messages', [])]
                
    def save(self):
        with open(self.file_path, "w") as f:
            json.dump({
                'users': [user.to_dict() for user in self.users],
                'channels': [channel.to_dict() for channel in self.channels],
                'messages': [message.to_dict() for message in self.messages]
            }, f)
    
    def get_users(self):
        return self.users

    def create_user(self, name):
        user = User(len(self.users)+1, name)
        self.users.append(user)
        self.save()
        return user
    
    def ban_user(self, name):
        user_to_ban = next((user for user in self.users if user.name==name), None)
        if not user_to_ban :
            print('No user to ban')
            return
        self.users.remove(user_to_ban)
        self.save()
    
    def create_channel(self, name):
        channel = Channel( len(self.channels)+1 ,name)
        self.channels.append(channel)
        self.save()
        return channel

    def get_channels(self):
        return self.channels
    
    def ban_channel(self, name):
        channel_to_ban = next((channel for channel in self.channels if channel.name == name), None)
        if not channel_to_ban:
            print('No channel to ban')
            return
        self.channels.remove(channel_to_ban)
        self.save()
    
    def send_messages(self, channel_id, content):
        message = Message(len(self.messages)+1, channel_id, content)
        self.messages.append(message)
        self.save()
        return message
    
    
class RemoteServer(BaseServer):
    def __init__(self, url):
        self.url = url

    def get_users(self):
        response = requests.get(self.url + "/users")  
        users = response.json()  
        return [User(id=user['id'], name=user['name']) for user in users]
    
    def create_user(self, name):
        response = requests.post(self.url + "/users/create", json={"name": name})

    def get_channels(self):
        response = requests.get(self.url + "/channels")
        channels = response.json()
        return [Channel(id=channel['id'], name=channel['name']) for channel in channels]
    
    def create_channel(self, name):
        response = requests.post(self.url + "/channels/create", json={"name":name})

    def get_channel_members(self, channel_id):
        response = requests.get(f"{self.url}/channels/{channel_id}/members")
        return response.json()

    def join_channel(self, channel_id, user_id, name):
        response = requests.post(f"{self.url}/channels/{channel_id}/join", json={"user_id": user_id, "name": name})
        print(f"L'utilisateur {name} (ID: {user_id}) a rejoint le canal {channel_id}.")
        return response.json()

    def get_all_messages(self):
        response = requests.get(f"{self.url}/messages", headers={"accept": "application/json"})
        return response.json()

    def get_messages(self, channel_id):
        response = requests.get(self.url + "/messages")
        messages = response.json()
        return [message for message in messages if message['channel_id'] == channel_id]
    
    def post_message(self, channel_id, sender_id, content):
        response = requests.post(f"{self.url}/channels/{channel_id}/messages/post", json={"sender_id": sender_id,"content": content})
        return response.json
    
class Client:  # MessengerApp

    @staticmethod
    def clearConsole():
        command = "clear"
        if os.name in ("nt", "dos"):
            command = "cls"
        os.system(command)

    def __init__(self, server):
        self.server = server

    def display_users(self):
        self.clearConsole()
        print('User list\n--------')
        users = self.server.get_users()  
        if not users:
          print("Aucun utilisateur trouvé.")
        else :
         for user in users:
          print(user)

    def display_channel_members(self):
        self.clearConsole()
        channel_id = int(input("Channel ID pour voir les membres : "))
        members = self.server.get_channel_members(channel_id)
        print(f"Utilisateurs dans le canal :  {channel_id}")
        if not members:
            print("Aucun utilisateur trouvé.")
        else:
            for member in members:
                print(f"ID: {member['id']}, Name: {member['name']}")

    def display_channels(self):
        self.clearConsole()
        print('Channel list\n--------')
        for channel in self.server.get_channels():
            print(channel)

    def join_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        channel_id = int(input("ID du canal à rejoindre: "))
        user_id = int(input("ID de l'utilisateur: "))
        name = input("Nom de l'utilisateur: ")
        self.server.join_channel(channel_id, user_id, name)
        
    
    def list_messages(self):
        self.clearConsole()
        messages = self.server.get_all_messages()
        if messages:
            print("\n Liste des messages :")
            for msg in messages:
                print(f"[{msg['reception_date']}] (Canal {msg['channel_id']}) Sender {msg['sender_id']} : {msg['content']}")
        else:
            print("Aucun message à afficher.")


    def display_messages(self, channel_id):
        self.clearConsole()
        print(f"Messages dans le canal {channel_id}")
        messages = self.server.get_messages(channel_id)  
        if not messages:
          print("Pas de messages dans ce channel.")
        else:
          for message in messages:
            print(f"Message ID: {message['id']}, Sender ID: {message['sender_id']}, Content: {message['content']}, Date: {message['reception_date']}")

    def create_user_menu(self):
        name = input('Name of the new user: ')
        self.server.create_user(name)
        print('New user created')
        self.display_users()

    def ban_user_menu(self):
        self.clearConsole()
        self.display_users()
        name = input('Name of the user to ban: ')
        self.server.ban_user(name)
        self.clearConsole()
        print(f'{name} ban')

    def create_channel_menu(self):
        self.clearConsole()
        name = input('Name of the new channel: ')
        self.server.create_channel(name)
        self.clearConsole()
        print('New channel created')

    def ban_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        name = input('name of the channel to ban: ')
        self.server.ban_channel(name)
        self.clearConsole()
        print(f'{name} ban')

    def send_message_menu(self):
        self.clearConsole()
        self.display_channels()
        try:
            channel_id = int(input("ID where to send the message: "))
            if channel_id not in [channel.id for channel in self.server.get_channels()]:
                print('Problem')
                return
            sender_id = int(input("ID de l'utilisateur envoyant le message : "))
            content = input('Message: ')
            self.server.post_message(channel_id, sender_id, content)
            self.clearConsole()
            print('Message sent')
        except ValueError:
            print('')
            return
    
    def main_menu (self):
        while True:
            print("\033[32m\n===================== Messenger =========================\033[0m")
            print("1. Voir tous les utilisateurs")
            print("2. Voir les utilisateurs d'un canal")
            print("3. Voir les canaux")
            print("4. Envoyer un message")
            print("5. Lire les canaux")
            print("6. Créer un utilisateur")
            print("7. Bannir un utilisateur")
            print("8. Créer un canal")
            print("9. Supprimer un canal ")
            print("10. Rejoindre un canal")
            print("11. Lister les messages")
            print("x. Quitter")

            choice = input("Choisissez une option : ")
            if choice == "1":
                self.display_users()
            elif choice == "2":
                self.display_channel_members()
            elif choice == "3":
                self.display_channels()
            elif choice == "4":
                self.send_message_menu()
            elif choice == "5":
                channel_id = int(input("Enter the channel ID to view messages: "))
                self.display_messages(channel_id)
            elif choice == "6":
                self.create_user_menu()
            elif choice == "7":
                self.ban_user_menu()
            elif choice == "8":
                self.create_channel_menu()
            elif choice == "9":
                self.ban_channel_menu()
            elif choice == "10":
                self.join_channel_menu()
            elif choice =="11":
                self.list_messages()
            elif choice == "x":
                print("Au revoir !")
                break
            else:
                print("Option invalide.")
    
# =================================== Main ===========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='Chemin du fichier JSON du serveur local')
    parser.add_argument('--url', help='URL du serveur distant')
    args = parser.parse_args()

    if args.server:
        print(f"Chargement du serveur local : {args.server}")
        server = Server(args.server)
        server.load()
    elif args.url:
        print(f"Connexion au serveur distant : {args.url}")
        server = RemoteServer(args.url)
    else:
        raise ValueError("Vous devez spécifier un fichier JSON local (--server) ou une URL distante (--url).")

    app = Client(server)
    app.main_menu()