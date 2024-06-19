from config import db

class User(db.Model):
    __tablename__ = 'cunts'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    cuntness = db.Column(db.BigInteger, unique=True, nullable=True)

    def __repr__(self):
        return f'<User: {self.name}, ID: {self.id}, Created at: {self.created_at}, Cuntness: {self.cuntness}>'


class Login(db.Model):
    __tablename__ = 'logins'
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    login = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, unique=False, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'<ID: {self.id}, Created at: {self.created_at}, Login: {self.login} ,Password: {self.password}, Email: {self.email}>'