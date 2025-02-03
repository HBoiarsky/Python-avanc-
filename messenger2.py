import json
import argparse
import os
import requests

class Entité: 
    def __init__(self, id: int, name: str):
       self.id=id
       self.name=name

    def __repr__(self):
        return f"{self.id}. {self.name}"

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
        print("\033[32mUser list\n--------\033[0m")
        users = self.server.get_users()  
        if not users:
            print("\033[31mAucun utilisateur trouvé.\033[0m")
        else:
            for user in users:
                print(f"\033[34m{user}\033[0m")

    def display_channel_members(self):
        self.clearConsole()
        channel_id = int(input("\033[33mChannel ID pour voir les membres : \033[0m"))
        members = self.server.get_channel_members(channel_id)
        print(f"\033[32mUtilisateurs dans le canal : {channel_id}\033[0m")
        if not members:
            print("\033[31mAucun utilisateur trouvé.\033[0m")
        else:
            for member in members:
                print(f"\033[34mID: {member['id']}, Name: {member['name']}\033[0m")

    def display_channels(self):
        self.clearConsole()
        print("\033[32mChannel list\n--------\033[0m")
        for channel in self.server.get_channels():
            print(f"\033[34m{channel}\033[0m")

    def join_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        channel_id = int(input("\033[33mID du canal à rejoindre: \033[0m"))
        user_id = int(input("\033[33mID de l'utilisateur: \033[0m"))
        name = input("\033[33mNom de l'utilisateur: \033[0m")
        self.server.join_channel(channel_id, user_id, name)
    
    def list_messages(self):
        self.clearConsole()
        messages = self.server.get_all_messages()
        if messages:
            print("\033[32m\n Liste des messages :\033[0m")
            for msg in messages:
                print(f"\033[34m[{msg['reception_date']}] (Canal {msg['channel_id']}) Sender {msg['sender_id']} : {msg['content']}\033[0m")
        else:
            print("\033[31mAucun message à afficher.\033[0m")


    def display_messages(self, channel_id):
        self.clearConsole()
        print(f"\033[32mMessages dans le canal {channel_id}\033[0m")
        messages = self.server.get_messages(channel_id)  
        if not messages:
            print("\033[31mPas de messages dans ce channel.\033[0m")
        else:
            for message in messages:
                print(f"\033[34mMessage ID: {message['id']}, Sender ID: {message['sender_id']}, Content: {message['content']}, Date: {message['reception_date']}\033[0m")

    def create_user_menu(self):
        name = input("\033[33mName of the new user: \033[0m")
        self.server.create_user(name)
        print("\033[32mNew user created\033[0m")
        self.display_users()

    def ban_user_menu(self):
        self.clearConsole()
        self.display_users()
        name = input("\033[33mName of the user to ban: \033[0m")
        self.server.ban_user(name)
        self.clearConsole()
        print(f"\033[32m{name} ban\033[0m")

    def create_channel_menu(self):
        self.clearConsole()
        name = input("\033[33mName of the new channel: \033[0m")
        self.server.create_channel(name)
        self.clearConsole()
        print("\033[32mNew channel created\033[0m")

    def ban_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        name = input("\033[33mName of the channel to ban: \033[0m")
        self.server.ban_channel(name)
        self.clearConsole()
        print(f"\033[32m{name} ban\033[0m")

    
    def send_message_menu(self):
        self.clearConsole()
        self.display_channels()
        try:
            channel_id = int(input("\033[33mID where to send the message: \033[0m"))
            if channel_id not in [channel.id for channel in self.server.get_channels()]:
                print("\033[31mProblem\033[0m")
                return
            sender_id = int(input("\033[33mID de l'utilisateur envoyant le message : \033[0m"))
            content = input("\033[33mMessage: \033[0m")
            self.server.post_message(channel_id, sender_id, content)
            self.clearConsole()
            print("\033[32mMessage sent\033[0m")
        except ValueError:
            print("\033[31m\nErreur de saisie.\033[0m")
            return
    
    def main_menu(self):
     while True:
        print("\033[32m\n===================== 📩 Messenger =========================\033[0m")
        print("\033[34m1. 👥 Voir tous les utilisateurs\033[0m")
        print("\033[34m2. 🔍 Voir les utilisateurs d'un canal\033[0m")
        print("\033[34m3. 🆕 Créer un utilisateur\033[0m")
        print("\033[34m4. 📢 Voir les canaux\033[0m")
        print("\033[34m5. 📜 Lire les messages d'un canal\033[0m")
        print("\033[34m6. 🔗 Rejoindre un canal\033[0m")
        print("\033[34m7. 🏗️ Créer un canal\033[0m")
        print("\033[34m8. 📨 Lister les messages\033[0m")
        print("\033[34m9. ✉️ Envoyer un message\033[0m")
        print("\033[34m10. 🚫 Bannir un utilisateur\033[0m")
        print("\033[34m11. ❌ Bannir un canal\033[0m")
        print("\033[31mx. Quitter\033[0m")

        choice = input("\033[33m🔸 Choisissez une option : \033[0m")  # Texte en jaune pour l'entrée utilisateur
        
        if choice == "1":
            self.display_users()
        elif choice == "2":
            self.display_channel_members()
        elif choice == "3":
            self.create_user_menu()
        elif choice == "4":
            self.display_channels()
        elif choice == "5":
            channel_id = int(input("\033[33m🔍 Entrez l'ID du canal pour voir les messages : \033[0m"))
            self.display_messages(channel_id)
        elif choice == "6":
            self.join_channel_menu()
        elif choice == "7":
            self.create_channel_menu()
        elif choice == "8":
            self.list_messages()
        elif choice == "9":
            self.send_message_menu()
        elif choice == "10":
            self.ban_user_menu()
        elif choice == "11":
            self.ban_channel_menu()
        elif choice == "x":
            print("\033[31m👋 Au revoir !\033[0m")
            break
        else:
            print("\033[31m❌ Option invalide. Veuillez réessayer.\033[0m")
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