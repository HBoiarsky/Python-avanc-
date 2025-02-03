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


