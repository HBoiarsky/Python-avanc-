from datetime import datetime

server = {
    'users': [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Third user'},
        {'id': 4, 'name': '4'},
        {'id': 5, 'name': '5 u'},
    ],
    'channels': [
        {'id': 1, 'name': 'Town square', 'member_ids': [1, 2]}
    ],
    'messages': [
        {
            'id': 1,
            'reception_date': datetime.now(),
            'sender_id': 1,
            'channel': 1,
            'content': 'Hi 👋'
        }
    ]
}

def create_user(name):
    n = len(server['users']) # n_id = max([d['id'] for d in server['users']]) + 1
    server['users'].append({'id': (n + 1), 'name': name})
    print('User created:', name)


# new_channel_users_string = 'Alice, Bob, Charlie'
# new_channel_users_string.split(',')
# [user.strip() for user in new_channel_users_string]


def display_users():
    print('User list\n--------')
    for user in server['users']:
        print(user['id'], user['name'])

def display_channels():
    print('Channel list\n--------')
    for channel in server['channels']:
        print(channel['id'], channel['name'])


def display_messages(choice):
    found = False
    for message in server['messages']:
        if message['channel'] == choice:
            print(f"Message ID: {message['id']}, Content: {message['content']}")
            found = True
    if not found:
        print("No messages in this channel.")

def main_menu():
    while True:
        print('=== Messenger ===')
        print('1. See users\n2. See channels\nx. Leave')
        choice = input('Select an option: ')
        
        if choice == 'x':
            print('Bye!')
            break
        elif choice == '1':
            display_users()
            user_menu()
        elif choice == '2':
            display_channels()
            choice = input('Select a group to see messages, 0 if not: ')
            if choice == '0':
                user_menu()
            else:
                try:
                    choice = int(choice)  
                    display_messages(choice)
                except ValueError:
                    print("Invalid input.")
        else:
            print('Unknown option:', choice)


def user_menu():
    print('\nn. Create user\nx. Main menu')
    choice = input('Select an option: ')
    if choice == 'n':
        name = input('Enter the name of the new user: ')
        create_user(name)
        display_users()  
    else:
        return  

if __name__ == "__main__":
    main_menu()


    