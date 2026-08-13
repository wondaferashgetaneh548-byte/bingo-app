from mongoengine import Document, StringField, IntField

class Student(Document):
    name = StringField(required=True, max_length=100)
    age = IntField(required=True)
    department = StringField(max_length=100)

    def __str__(self):
        return self.name

