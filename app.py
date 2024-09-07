from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_session import Session
import MySQLdb.cursors
import re
import time

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'plygrnd_byhr_db'
app.config['MYSQL_DB'] = 'byhr_db'

mysql = MySQL(app)

# Session management configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = '5cfabe1beb88a6c88f0be5f06a11241b'
Session(app)

# Dictionary to track log in attempts
log_in_attempts = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['psw']
        password_repeat = request.form['psw_repeat']
        
        # Check if passwords match
        if password != password_repeat:
            flash('Passwords do not match!')
            return redirect(url_for('register'))
        

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email))
            mysql.connection.commit()
            cursor.close()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('log_in'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error: Could not register. Please try again.')
            return redirect(log_in('log_in'))
            
        else:
            flash('Hindi pareho ang inilagay mo sa password!', 'danger')
                
    return render_template('register.html')

@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        remember = request.form.get('remember')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s OR username = %s', (email_or_username, email_or_username))
        account = cursor.fetchone()

        if account:
            if log_in_attempts.get(email_or_username, 0) >= 5:
                flash('Madaming beses mo nang sinubok na pumasok sa account na ito. Subukan mo uli pakatapos ang isang minuto.', 'danger')
                time.sleep(60)
                log_in_attempts[email_or_username] = 0

            if account['password'] == password:
                session['loggedin'] = True
                session['username'] = account['username']
                session['email'] = account['email']
                session['remember'] = remember == 'on'

                log_in_attempts.pop(email_or_username, None)
                return redirect(url_for('index'))
            
            else:
                flash('Mali ang password na inilagay!', 'danger')
                log_in_attempts[email_or_username] = log_in_attempts.get(email_or_username, 0) + 1
        
        else:
            flash('Hindi mahanap sa database ang email o username na inilagay')

    return render_template('log_in.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('remember', None)
    return redirect(url_for('log_in'))

if __name__ == "__main__":
    app.run(debug=True)