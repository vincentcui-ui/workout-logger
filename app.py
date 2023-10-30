from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout_tracker.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random string in a real application

db = SQLAlchemy(app)
#db.engine.execute("PRAGMA foreign_keys=ON;")
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # This will store the hashed password

class Exercise(db.Model):
    exercise_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)

class Workout(db.Model):
    workout_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes

class WorkoutDetail(db.Model):
    detail_id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.workout_id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.exercise_id'), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # Duration in minutes for cardio exercises
    weight = db.Column(db.Float, nullable=True)  # Weight for strength exercises

from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    else:
        return render_template('index.html')  # This can be a welcome page or promotional page for users not logged in

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        
        # Create new user instance and add to the database
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Fetch the user by email
        user = User.query.filter_by(email=email).first()
        
        # Check user and password hash
        if user and check_password_hash(user.password, password):
            flash('Login successful!')
            session['user_id'] = user.user_id
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check email and password.')
        
    return render_template('login.html')

@app.route('/add_workout', methods=['GET', 'POST'])
def add_workout():
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        date_str = request.form.get('date')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        duration = int(request.form.get('duration'))
        
        # Create new workout instance and add to the database
        user_id = session.get('user_id')
        new_workout = Workout(user_id=user_id, date=date_obj, total_duration=duration)

        db.session.add(new_workout)
        db.session.commit()
        
        flash('Workout added successfully!')
        return redirect(url_for('index'))
        
    return render_template('add_workout.html')

@app.route('/list_workouts')
def list_workouts():
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    workouts = Workout.query.filter_by(user_id=session['user_id']).all()
    return render_template('list_workouts.html', workouts=workouts)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)