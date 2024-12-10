import json

class Entité: 
    def __init__(self, id: int, name: str):
       self.id=id
       self.name=name

    def __repr__(self) -> str:
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
    
    def create_channels(self, name):
        channel = Channel( len(self.channels)+1 ,name)
        self.channels.append(channel)
        self.save()
        return channel
    
    def send_messages(self, channel_id, content):
        message = Message(len(self.messages)+1, channel_id, content)
        self.messages.append(message)
        self.save()
        return message


class MessengerApp :
    def __init__(self, server):
        self.server = server

    def display_users(self):
        print('User list\n--------')
        for user in self.server.users :
          print(user)

    def display_channels(self):
        print('Channel list\n--------')
        for channel in self.server.channels:
            print(channel)

    def display_messages(self, channel_id):
         found = False
         for message in self.server.messages:
           if message.channel_id == channel_id:
                 print(f"Message ID: {message.id}, Content: {message.content}")
                 found = True
           if not found:
                 print("Pas de messages dans ce channel.")

    def channel_list_screen(self):
        self.display_channels()
        choice = input('Select a group to see messages, 0 if not: ')
        if choice == '0':
           return self.main_menu()

        try:
           choice = int(choice)
           self.display_messages(choice)
        except ValueError:
           print("Invalid input.")

    def main_menu (self):
        while True:
            print('=== Messenger ===')
            print('1. See users\n2. See channels\n3. Send/view messages\nx. Leave')
            choice = input('Select an option: ')
        
            if choice == 'x':
                print('Au revoir!')
                break
            elif choice == '1':
                self.display_users()
                self.user_menu()
            elif choice == '2':
                self.display_channels()
                self.channel_menu()
            elif choice == '3':
                self.channel_list_screen()
            else:
                print('Unknown option:', choice)

    def user_menu(self):
        while True :
          print('\nn. Create user\nx. Main menu')
          choice = input('Select an option: ')
          if choice == 'n':
              name = input('Enter the name of the new user: ')
              self.server.create_user(name)
              self.display_users()  
          elif choice == 'x':
              break      


    def channel_menu(self):
        while True: 
           print('\nn. Create channel\nx. Main menu')
           choice = input('Select an option')
           if choice == 'n': 
            name = input("Entrer le nom du channel")
            self.server.create_channels(name)
            self.display_channels()
           elif choice == 'x':
            break
 
    def message_menu(self):
        self.display_channels()
        channel_id = int(input('Select channel id:'))
        content = input('Enter your message')
        self.server.send_messages(channel_id, content)


# === Main ===
if __name__ == "__main__":
   server = Server ("/Users/honoreboiarsky/Documents/python avancé 2/messenger2.json")
   server.load()
   app = MessengerApp(server)
   app.main_menu()


   