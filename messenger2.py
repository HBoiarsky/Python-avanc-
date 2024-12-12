import json
import os

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

class Server :
    def __init__(self, file_path):
        self.file_path = file_path
        self.users = []
        self.channels = []
        self.messages = []

    def load(self):
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
        for user in self.server.users :
          print(user)

    def display_channels(self):
        self.clearConsole()
        print('Channel list\n--------')
        for channel in self.server.channels:
            print(channel)

    def display_messages(self, channel_id):
        self.clearConsole()
        print(f"Messages dans le canal {channel_id}")
        found = False
        for message in self.server.messages:
           if message.channel_id == channel_id:
                 print(f"Message ID: {message.id}, Content: {message.content}")
                 found = True
        if not found:
                 print("Pas de messages dans ce channel.")

    def create_user_menu(self):
        self.clearConsole()
        name = input('Name of the new user: ')
        self.server.create_user(name)
        self.clearConsole()
        print('New user created')

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
            if channel_id not in [channel.id for channel in self.server.channels]:
                print('Problem')
                return
            content = input('Message: ')
            self.server.send_messages(channel_id, content)
            self.clearConsole()
            print('Message sent')
        except ValueError:
            print('')
            return


    def main_menu (self):
        while True:
            print("\n====== Messenger ======")
            print("1. Voir les utilisateurs")
            print("2. Voir les canaux")
            print("3. Envoyer un message")
            print("4. Créer un utilisateur")
            print("5. Bannir un utilisateur")
            print("6. Créer un canal")
            print("7. Supprimer un canal ")
            print("x. Quitter")

            choice = input("Choisissez une option : ")
            if choice == "1":
                self.display_users()
            elif choice == "2":
                self.display_channels()
            elif choice == "3":
                self.send_message_menu()
            elif choice == "4":
                self.create_user_menu()
            elif choice == "5":
                self.ban_user_menu()
            elif choice == "6":
                self.create_channel_menu()
            elif choice == "7":
                self.ban_channel_menu()
            elif choice == "x":
                print("Au revoir !")
                break
            else:
                print("Option invalide.")

# ============= Main =============
if __name__ == "__main__":
   server = Server ("/Users/honoreboiarsky/Documents/python avancé 2/messenger2.json")
   server.load()
   app = Client(server)
   app.main_menu()
