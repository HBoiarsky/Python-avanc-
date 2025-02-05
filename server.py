import json
import requests
from model import User, Channel, Message

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
            self.messages = [Message(sender_id=message['sender_id'], channel_id=message['channel'], content=message['content']) for message in server.get('messages', [])]


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
        if any(user.name == name for user in self.users):
            print(f"\033[34mErreur: L'utilisateur {name} existe déjà.\033[0m")
            return None
    
        used_ids = {user.id for user in self.users}
        new_id = 1
        while new_id in used_ids:
            new_id += 1
    
        user = User(new_id, name)
        self.users.append(user)
        self.save()
        return user
    
    def ban_user(self, name):
        user_to_ban = next((user for user in self.users if user.name == name), None)
        if not user_to_ban:
            print('No user to ban')
            return
    
        self.users.remove(user_to_ban)
        self.save()

    def get_channels(self):
        return self.channels
    
    def create_channel(self, name):
        channel = Channel( len(self.channels)+1 ,name)
        self.channels.append(channel)
        self.save()
        return channel

    def ban_channel(self, name):
        channel_to_ban = next((channel for channel in self.channels if channel.name == name), None)
        if not channel_to_ban:
            print('No channel to ban')
            return
        self.channels.remove(channel_to_ban)
        self.save()

    def get_channel_members(self, channel_id):
        channel = next((channel for channel in self.channels if channel.id == channel_id), None)
        if not channel:
            print(f"\033[34mErreur: Le canal {channel_id} n'existe pas.\033[0m")
            return []
        return channel.members

    def join_channel(self, channel_id, user_name):
        user = next((user for user in self.users if user.name == user_name), None)
        if not user:
            print(f"\033[34mErreur: L'utilisateur {user_name} n'existe pas.\033[0m")
            return

        channel = next((channel for channel in self.channels if channel.id == channel_id), None)
        if not channel:
            print(f"\033[34mErreur: Le canal {channel_id} n'existe pas.\033[0m")
            return

        if user in channel.members:
            print(f"\033[34m{user_name} est déjà dans le canal {channel_id}.\033[0m")
            return

        channel.members.append(user)
        print(f"\033[34m{user_name} (ID: {user.id}) a rejoint le canal {channel_id}.\033[0m")
        self.save()

    def get_all_messages(self):
        for message in self.messages:
            user = next((user for user in self.users if user.id == message.sender_id), None)
            message.sender_name = user.name if user else "Unknown"
        return self.messages

    def get_messages(self, channel_id):
        messages = [message for message in self.messages if message.channel_id == channel_id]
        for message in messages:
            user = next((user for user in self.users if user.id == message.sender_id), None)
            message.sender_name = user.name if user else "Unknown"
        return messages    

    def post_message(self, channel_id, sender_name, content):
        user = next((user for user in self.users if user.name == sender_name), None)
        if not user:
            print(f"\033[31mErreur : L'utilisateur {sender_name} n'existe pas.\033[0m")
            return
    
        message = Message(user.id, channel_id, content)
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

        users_response = requests.get(self.url + "/users")
        users = users_response.json()
        user = next((user for user in users if user["name"] == name), None)
        if not user:
            print(f"\033[34mErreur: L'utilisateur {name} n'existe pas.\033[0m")
            return

        user_id = user["id"]

        channels_response = requests.get(f"{self.url}/channels")
        channels = channels_response.json()
        channel = next((channel for channel in channels if channel["id"] == channel_id), None)
        if not channel:
            print(f"\033[34mErreur: Le canal {channel_id} n'existe pas.\033[0m")
            return

        response = requests.post(f"{self.url}/channels/{channel_id}/join", json={"user_id": user_id, "name": name})
        print(f"\033[34mL'utilisateur {name} (ID: {user_id}) a rejoint le canal {channel_id}.\033[0m")
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


