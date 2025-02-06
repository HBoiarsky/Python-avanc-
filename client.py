import os
from server import Server, RemoteServer

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
        self.display_channels()
        channel_id = int(input("\033[33mChannel ID : \033[0m"))
        self.clearConsole()
        members = self.server.get_channel_members(channel_id)
        if not members:
            print("\033[31mAucun utilisateur trouvé.\033[0m")
        else:
            for member in members:
                    if isinstance(member, dict):
                        print(f"\033[34mNom: {member['name']} (ID: {member['id']})\033[0m")
                    else:
                        print(f"\033[34mNom: {member.name} (ID: {member.id})\033[0m")
                
    def display_channels(self):
        self.clearConsole()
        print("\033[32mChannel list\n--------\033[0m")
        for channel in self.server.get_channels():
            print(f"\033[34m{channel}\033[0m")

    def join_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        channel_id = int(input("\033[33mID du canal à rejoindre : \033[0m"))
        if channel_id not in [channel.id for channel in self.server.get_channels()]:
            print("\033[31mCanal invalide.\033[0m")
            return
        
        user_name = input("\033[33mNom de l'utilisateur : \033[0m") 
        if user_name not in [user.name for user in self.server.get_users()]:
            print("\033[31mUtlisateur invalide.\033[0m")
            return

        self.clearConsole()
        self.server.join_channel(channel_id, user_name)  


    def list_messages(self):
        self.clearConsole()
        messages = self.server.get_all_messages()
        if messages:
            print("\033[32m\n Liste des messages :\033[0m")
            for message in messages:
                if isinstance(message, dict):  
                    print(f"\033[34m[{message['reception_date']}] (Canal {message['channel_id']}) Sender {message['sender_name']} : {message['content']}\033[0m")
                else:
                    print(f"\033[34m(Canal {message.channel_id}) Sender {message.sender_name} : {message.content}\033[0m")
        else:
            print("\033[31mAucun message à afficher.\033[0m")

    def display_messages(self, channel_id):
        print(f"\033[32mMessages dans le canal {channel_id}\033[0m")
        messages = self.server.get_messages(channel_id)  
        if not messages:
            print("\033[31mPas de message dans ce canal.\033[0m")
        else:
            for message in messages:
                if isinstance(message, dict):  
                    sender_name = message.get('sender_name', "Unknown")
                    print(f"\033[34mSender {sender_name} : {message['content']}\033[0m")
                else:
                    print(f"\033[34mSender {message.sender_name} : {message.content}\033[0m")

    def create_user_menu(self):
        self.clearConsole()
        self.display_users()
        name = input("\033[33mName of the new user: \033[0m")
        self.server.create_user(name)
        print("\033[32mNew user created\033[0m")
        self.display_users()

    def ban_user_menu(self):
        self.clearConsole()
        self.display_users()
        name = input("\033[33mName of the user to ban: \033[0m")
        self.server.ban_user(name)

    def create_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        name = input("\033[33mName of the new channel: \033[0m")
        self.server.create_channel(name)
        

    def ban_channel_menu(self):
        self.clearConsole()
        self.display_channels()
        name = input("\033[33mName of the channel to ban: \033[0m")
        self.server.ban_channel(name)
    
    def send_message_menu(self):
        self.clearConsole()
        self.display_channels()
        channel_id = int(input("\033[33mID du canal où envoyer le message : \033[0m"))
        if channel_id not in [channel.id for channel in self.server.get_channels()]:
            print("\033[31mCanal invalide.\033[0m")
            return
        
        sender_name = input("\033[33mNom de l'utilisateur envoyant le message : \033[0m")
        if sender_name not in [user.name for user in self.server.get_users()]:
            print("\033[31mUtlisateur invalide.\033[0m")
            return
        content = input("\033[33mMessage : \033[0m")
        
        self.server.post_message(channel_id, sender_name, content)
        self.clearConsole()
        print("\033[32mMessage envoyé\033[0m")

    
    def main_menu(self):
     while True:
        print("\033[32m\n===================== 📩 Messenger =========================\033[0m")
        print("\033[32m\n============================================================\033[0m")
        print()
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
        print()
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
            self.clearConsole()
            self.display_channels()
            channel_id = int(input("\033[33m🔍 Entrez l'ID du canal pour voir les messages : \033[0m"))
            if channel_id not in [channel.id for channel in self.server.get_channels()]:
                print("\033[31mCanal invalide.\033[0m")
            else :
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