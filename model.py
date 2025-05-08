import json

class Entité:
    """Classe de base représentant une entité avec un ID et un nom."""
    def __init__(self, id: int, name: str):
       self.id=id
       self.name=name

    def __repr__(self) -> str:
        return f"{self.id}. {self.name}"

class User(Entité):
    """Représente un utilisateur."""
    def to_dict(self) -> dict:
        """Convertit l'utilisateur en dictionnaire."""
        return {"id": self.id, "name": self.name}

class Channel(Entité):
    """Représente un canal avec des membres."""
    def __init__(self, id: int, name: str):
        super().__init__(id, name)
        self.members: list[User] = []

    def to_dict(self) -> dict:
        """Convertit le canal en dictionnaire."""
        return {"id": self.id, "name": self.name, "members": [{"id": member.id, "name": member.name} for member in self.members]}

class Message():
    """Représente un message envoyé dans un canal."""
    def __init__(self, sender_id: int, channel_id: int, content: str):
        # Il manque l'horodatage du message, que vous pouvez représenter
        # par un objet de la classe `datetime` issu de la bibliothèque
        # du même nom.
        self.sender_id = sender_id
        self.channel_id = channel_id
        self.content = content
        self.sender_name = None

    def __repr__(self) -> str:
        return f"(Canal {self.channel_id}) {self.sender_name or 'Unknown'} : {self.content}"

    def to_dict(self) -> dict:
        """Convertit le message en dictionnaire."""
        return {"sender_id": self.sender_id, "channel": self.channel_id, "content": self.content}
