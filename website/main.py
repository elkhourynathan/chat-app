from os import path
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_socketio import SocketIO, send

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp'

# Initialize database
db = SQLAlchemy()
DB_NAME = 'database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)

# SocketIO
socketIO = SocketIO(app, cors_allowed_origins="*")

@socketIO.on('message')
def sendMessage(message):
    
    send(message, broadcast=True)

# Routes
    
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', user=current_user)

@app.route("/current_user", methods=['GET', 'POST'])
def get_current_user():
    return {"user": current_user.displayName}

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('home'))
    return render_template('login.html', user=current_user)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        displayName = request.form.get('displayName')
        password = request.form.get('password')
        password1 = request.form.get('password1')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email must unique.', category='error')
        elif len(email) < 10:
            flash('Email must be greater than 10 characters.', category='error')
        elif len(password) < 3:
            flash('Password must be greater than 3 characters.', category='error')
        elif password != password1:
            flash('Passwords do not match.', category='error')
        else:
            created_user = User(email=email, displayName=displayName, password=generate_password_hash(password, method='sha256'))
            db.session.add(created_user)
            db.session.commit()
            flash('Account created.', category='success')
            login_user(created_user, remember=True)
            return redirect(url_for('home'))

    return render_template('signup.html', user=current_user)



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Create database

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        
create_database(app)

@app.before_first_request
def create_tables():
    db.create_all()
    
# Initalize login manager
        
loginManager = LoginManager()
loginManager.login_view = 'login'
loginManager.init_app(app)

@loginManager.user_loader
def loadUser(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(300), unique=True)
    displayName = db.Column(db.String(300))
    password = db.Column(db.String(300))


if __name__ == '__main__':
    app.run(port=8000, debug=True)