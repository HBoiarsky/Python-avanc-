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



def load_server():
  with open("/Users/honoreboiarsky/Documents/python avancé 2/messenger2.json", "r") as f:
    server = json.load(f)
    server['users'] = [User(user['id'], user['name']) for user in server['users']]
    return server

server = load_server()

## server['users'] : list[dict]
## Transfomer server['users'] en list[User]

def save_json():
   server['users'] = [user.to_dict() for user in server['users']]
   with open("/Users/honoreboiarsky/Documents/python avancé 2/messenger2.json", "w") as f:
      json.dump(server, f)


# === Utilisateurs ===
def create_user(name):
    id = len(server['users']) + 1
    new_user = User(id, name)
    server['users'].append(new_user)
    save_json()
    print('Utilisateur créee: ')

def display_users():
    print('User list\n--------')
    for user in server['users']:
        print(user.id, user.name)


# === Canaux ===
def create_channels(name):
    n = len(server['channels'])
    server['channels'].append({'id': n+1, 'name': name})
    save_json()
    print(f"Channel crée: {name}")

def display_channels():
    print('Channel list\n--------')
    for channel in server['channels']:
        print(channel['id'], channel['name'])


#  === Messages ===
def display_messages(channel_id):
    found = False
    for message in server['messages']:
        if message['channel'] == channel_id:
            print(f"Message ID: {message['id']}, Content: {message['content']}")
            found = True
    if not found:
        print("Pas de messages dans ce channel.")

def send_messages(channel_id, content):
    n = len(server['messages'])
    server['messages']. append({'id': n+1, 'channel': channel_id, 'content': content})
    save_json()
    print("Message envoyé")


# === Menu ===
def channel_list_screen():
    display_channels()
    choice = input('Select a group to see messages, 0 if not: ')
    if choice == '0':
        return main_menu()

    try:
        choice = int(choice)
        display_messages(choice)
    except ValueError:
        print("Invalid input.")

def main_menu():
    while True:
        print('=== Messenger ===')
        print('1. See users\n2. See channels\n3. Send/view messages\nx. Leave')
        choice = input('Select an option: ')
        
        if choice == 'x':
            print('Au revoir!')
            break
        elif choice == '1':
            display_users()
            user_menu()
        elif choice == '2':
            display_channels()
            channel_menu()
        elif choice == '3':
            channel_list_screen()
        else:
            print('Unknown option:', choice)


def user_menu():
    while True :
        print('\nn. Create user\nx. Main menu')
        choice = input('Select an option: ')
        if choice == 'n':
           name = input('Enter the name of the new user: ')
           create_user(name)
           display_users()  
        elif choice == 'x':
           break  



def channel_menu():
    while True : 
        print('\nn. Create channel\ns. Send messages\nx. Main menu')
        choice = input('Select an option')
        if choice == 'n': 
            name = input("Entrer le nom du channel")
            create_channels(name)
            display_channels()
        elif choice =='s':
            display_channels()
            channel_id = int(input('Select channel id:'))
            content = input('Enter your message')
            send_messages(channel_id, content)
        elif choice == 'x':
            break


# === Main ===
if __name__ == "__main__":
   main_menu()