import json

class Entité: 
    def __init__(self, id, name):
       self.id=id
       self.name=name

    def __repr__(self):
        return f"{self.id}. {self.name}"

class User(Entité):
    def to_dict(self):
        return {"id": self.id, "name": self.name}

class Channel(Entité):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.members = []

    def to_dict(self):
        return {"id": self.id, "name": self.name, "members": [{"id": member.id, "name": member.name} for member in self.members]}

class Message():
    def __init__(self, sender_id, channel_id, content):
        self.sender_id = sender_id
        self.channel_id = channel_id
        self.content = content
        self.sender_name = None  

    def __repr__(self):
        return f"(Canal {self.channel_id}) {self.sender_name or 'Unknown'} : {self.content}"

    def to_dict(self):
        return {"sender_id": self.sender_id, "channel": self.channel_id, "content": self.content}