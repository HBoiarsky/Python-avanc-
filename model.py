import json

class Entité: 
    """Classe de base représentant une entité avec un ID et un nom."""
    def __init__(self, id, name):
       self.id=id
       self.name=name

    def __repr__(self):
        return f"{self.id}. {self.name}"

class User(Entité):
    """Représente un utilisateur."""
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire."""
        return {"id": self.id, "name": self.name}

class Channel(Entité):
    """Représente un canal avec des membres."""
    def __init__(self, id, name):
        super().__init__(id, name)
        self.members = []

    def to_dict(self):
        """Convertit le canal en dictionnaire."""
        return {"id": self.id, "name": self.name, "members": [{"id": member.id, "name": member.name} for member in self.members]}

class Message():
    """Représente un message envoyé dans un canal."""
    def __init__(self, sender_id, channel_id, content):
        self.sender_id = sender_id
        self.channel_id = channel_id
        self.content = content
        self.sender_name = None  

    def __repr__(self):
        return f"(Canal {self.channel_id}) {self.sender_name or 'Unknown'} : {self.content}"

    def to_dict(self):
        """Convertit le message en dictionnaire."""
        return {"sender_id": self.sender_id, "channel": self.channel_id, "content": self.content}