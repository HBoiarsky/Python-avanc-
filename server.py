from abc import ABC, abstractmethod
from typing import List
import json
import requests
from model import User, Channel, Message

class BaseServer(ABC):
    @abstractmethod
    def get_users(self) -> List[User]:
        """Récupère tous les utilisateurs."""
        pass

    def create_user(self, name : str) -> User:
        """Crée un utilisateur."""
        pass

    @abstractmethod
    def get_channels(self) -> List[Channel]:
        """Récupère tous les canaux."""
        pass

    @abstractmethod
    def create_channel(self, name: str) -> Channel:
        """Crée un canal."""
        pass

    @abstractmethod
    def get_channel_members(self, channel_id : int) -> List[User]:
        """Récupère tous les utilisateurs d'un canal."""
        pass

    @abstractmethod
    def join_channel(self, channel_id : int, user_name : str):
        """Ajoute un utilisateur à un canal."""
        pass

    @abstractmethod
    def get_all_messages(self) -> List[Message]:
        """Récupère tous les messages."""
        pass

    @abstractmethod
    def get_messages(self, channel_id : int) -> List[Message]:
        """Récupère tous les messages d'un canal."""
        pass

    @abstractmethod
    def post_message(self, channel_id : int, sender_name : str, content : str) -> Message:
        """Poste un message dans un canal."""
        pass

class Server(BaseServer) :
    def __init__(self, file_path : str):
        self.file_path = file_path
        self.users = []
        self.channels = []
        self.messages = []
        self.load()
     
    # Méthodes spécifiques au serveur local
    def load(self):
        if not self.file_path:
            raise ValueError("Le chemin du fichier JSON est manquant. Utilisez l'argument --server pour spécifier un fichier.")
        with open(self.file_path, "r") as f:
            server = json.load(f)
            self.users = [User(id=user['id'], name=user['name']) for user in server.get('users', [])]
            self.channels = [Channel(id=channel['id'], name=channel['name']) for channel in server.get('channels', [])]
            self.messages = [Message(sender_id=message['sender_id'], channel_id=message['channel'], content=message['content']) for message in server.get('messages', [])]


    def save(self):
        with open(self.file_path, "w") as f:
            json.dump({
                'users': [user.to_dict() for user in self.users],
                'channels': [channel.to_dict() for channel in self.channels],
                'messages': [message.to_dict() for message in self.messages]
            }, f)
    
    # Méthodes abstraites implémentées
    def get_users(self) -> List[User]:
        return self.users

    def create_user(self, name : str) -> User:
        if any(user.name == name for user in self.users):
            print(f"\033[31mErreur: L'utilisateur {name} existe déjà.\033[0m")
            input("\033[33mAppuyez sur Entrée pour continuer...\033[0m")
            return
    
        used_ids = {user.id for user in self.users}
        new_id = 1
        while new_id in used_ids:
            new_id += 1
    
        user = User(new_id, name)
        self.users.append(user)
        self.save()
        return user
    
    def ban_user(self, name : str):
        user_to_ban = next((user for user in self.users if user.name == name), None)
        if not user_to_ban:
            print("\033[31mUtilisateur introuvable.\033[0m")
            return  

        self.users.remove(user_to_ban)
        self.save()
        print(f"\033[32mL'utilisateur {name} a été banni avec succès.\033[0m")

    def get_channels(self) -> List[Channel]:
        return self.channels
    
    def create_channel(self, name : str) -> Channel:
        channel = next((channel for channel in self.channels if channel.name == name), None)
        if channel:
            print(f"\033[31mErreur: Le canal '{name}' existe déjà.\033[0m")
            input("\033[33mAppuyez sur Entrée pour continuer...\033[0m")
            return
        
        new_id = max((c.id for c in self.channels), default=0) + 1
        channel = Channel(new_id, name)
        print(f"\033[32mLe canal '{name}' a été crée.\033[0m")
        self.channels.append(channel)
        self.save()
        return channel


    def ban_channel(self, name : str):
        channel_to_ban = next((channel for channel in self.channels if channel.name == name), None)
        if not channel_to_ban:
            print(f"\033[31mCanal introuvable.\033[0m")
            return
    
        self.channels.remove(channel_to_ban)
        self.messages = [message for message in self.messages if message.channel_id != channel_to_ban.id]
        self.save()
        print(f"\033[32mLe canal '{name}' a été banni avec succès.\033[0m")


    def get_channel_members(self, channel_id : int) -> List[User]:
        channel = next((channel for channel in self.channels if channel.id == channel_id), None)
        if not channel:
            print(f"\033[34mErreur: Le canal {channel_id} n'existe pas.\033[0m")
            return []
        return channel.members

    def join_channel(self, channel_id : int, user_name : str):
        user = next((user for user in self.users if user.name == user_name), None)
        channel = next((channel for channel in self.channels if channel.id == channel_id), None)

        if user in channel.members:
            print(f"\033[34m{user_name} est déjà dans le canal {channel_id}.\033[0m")
            return

        channel.members.append(user)
        print(f"\033[34m{user_name} (ID: {user.id}) a rejoint le canal {channel_id}.\033[0m")
        self.save()

    def get_all_messages(self) -> List[Message]:
        for message in self.messages:
            user = next((user for user in self.users if user.id == message.sender_id), None)
            message.sender_name = user.name if user else "Unknown"
        return self.messages

    def get_messages(self, channel_id : int) -> List[Message]:
        messages = [message for message in self.messages if message.channel_id == channel_id]
        for message in messages:
            user = next((user for user in self.users if user.id == message.sender_id), None)
            message.sender_name = user.name if user else "Unknown"
        return messages    

    def post_message(self, channel_id : int, sender_name : str, content : str) -> Message:
        user = next((user for user in self.users if user.name == sender_name), None)
        message = Message(user.id, channel_id, content)
        self.messages.append(message)
        self.save()
        return message
    
    
class RemoteServer(BaseServer):
    def __init__(self, url):
        self.url = url

    # Implémentation des méthodes abstraites
    def get_users(self) -> List[User]:
        response = requests.get(self.url + "/users")  
        users = response.json()  
        return [User(id=user['id'], name=user['name']) for user in users]
    
    def create_user(self, name : str) -> User:
        users_response = requests.get(self.url + "/users")  
        users = users_response.json()
        if any(user["name"] == name for user in users):
            print(f"\033[31mErreur: L'utilisateur {name} existe déjà.\033[0m")
            return

        response = requests.post(self.url + "/users/create", json={"name": name})
        if response.status_code == 200:
            print(f"\033[32mL'utilisateur {name} a été créé avec succès.\033[0m")
        else:
            print(f"\033[31mErreur lors de la création de l'utilisateur {name}.\033[0m")   

    def get_channels(self) -> List[Channel]:
        response = requests.get(self.url + "/channels")
        channels = response.json()
        return [Channel(id=channel['id'], name=channel['name']) for channel in channels]
    
    def create_channel(self, name : str) -> Channel:
        channels_response = requests.get(f"{self.url}/channels")
        channels = channels_response.json()
        channel = next((channel for channel in channels if channel["name"] == name), None)
        if channel:
            print(f"\033[31mErreur: Le canal {name} existe déjà.\033[0m")
            return
        response = requests.post(self.url + "/channels/create", json={"name":name})
        print(f"\033[32mLe canal {name} a été crée avec succès.\033[0m")


    def get_channel_members(self, channel_id : int) -> List[User]:
        response = requests.get(f"{self.url}/channels/{channel_id}/members")
        return response.json()

    def join_channel(self, channel_id : int, user_name : str):
        users_response = requests.get(self.url + "/users")
        users = users_response.json()
        user = next((user for user in users if user["name"] == user_name), None)
    
        user_id = user["id"]

        members = self.get_channel_members(channel_id)
        if any(member.get("id") == user_id for member in members):
            print(f"\033[34m{user_name} est déjà dans le canal {channel_id}.\033[0m")
            return

        response = requests.post(f"{self.url}/channels/{channel_id}/join", json={"user_id": user_id, "name": user_name})
        if response.status_code == 200:
            print(f"\033[32m{user_name} a rejoint le canal {channel_id}.\033[0m")
        else:
            print(f"\033[31mErreur lors de la jonction au canal : {response.text}\033[0m")

    def get_all_messages(self) -> List[Message]:
        response = requests.get(f"{self.url}/messages", headers={"accept": "application/json"})
        messages = response.json()
        for message in messages:
            user_response = requests.get(f"{self.url}/users/{message['sender_id']}")
            user = user_response.json()
            message['sender_name'] = user['name'] if user else "Unknown"
        return messages

    def get_messages(self, channel_id : int) -> List[Message]:
        response = requests.get(f"{self.url}/messages")
        messages = response.json()
        for message in messages:
            if message['channel_id'] == channel_id:
                user_response = requests.get(f"{self.url}/users/{message['sender_id']}")
                user = user_response.json()
                message['sender_name'] = user['name'] if user else "Unknown"
        return [message for message in messages if message['channel_id'] == channel_id]

    def post_message(self, channel_id : int, sender_name : str, content : str) -> Message:
        users_response = requests.get(self.url + "/users")
        users = users_response.json()
        user = next((user for user in users if user['name'] == sender_name), None)

        members = requests.get(f"{self.url}/channels/{channel_id}/members").json()
        if not any(m['id'] == user['id'] for m in members):
            print(f"\033[31mErreur: {sender_name} doit rejoindre le canal avant d'envoyer des messages.\033[0m")
            return None
        response = requests.post(f"{self.url}/channels/{channel_id}/messages/post", json={"sender_id": user['id'],"content": content})
        if response.status_code == 200:
            print(f"\033[32mMessage envoyé avec succès dans le canal {channel_id}.\033[0m")
        else:
            print(f"\033[31mErreur lors de l'envoi du message.\033[0m")


  