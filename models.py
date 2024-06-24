from config import db

class Login(db.Model):
    __tablename__ = 'logins'
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    login = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, unique=False, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'<ID: {self.id}, Created at: {self.created_at}, Login: {self.login} ,Password: {self.password}, Email: {self.email}>'

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    report = db.Column(db.Text, unique=False, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('logins.id'), nullable=False)
    user = db.relationship('Login', backref=db.backref('reports', lazy=True))

    def __repr__(self):
        return f'<ID: {self.id}, Created at: {self.created_at}, Report: {self.report}, User ID: {self.user_id}>'