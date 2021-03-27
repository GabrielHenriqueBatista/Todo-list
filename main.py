import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""
  CREATE TABLE IF NOT EXISTS todos (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    complete INTEGER,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users (id)
  )
""")

cursor.execute("""
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
  )
""")

conn.close()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'

@app.route('/')
def index():
  if not 'user_id' in session:
    return redirect('/login')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'SELECT * FROM todos WHERE user_id = ?',
    (session['user_id'],)
  )
  todos = cursor.fetchall()
  conn.close()
  return render_template('index.html', todos=todos)

@app.route('/create', methods=['POST'])
def create():
  if not 'user_id' in session:
    return redirect('/login')

  title = request.form.get('title')
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'INSERT INTO todos (title, complete, user_id) VALUES (?, ?, ?)',
    (title, 0, session['user_id'])
  )
  conn.commit()
  conn.close()
  return redirect('/')

@app.route('/delete/<id>')
def delete(id):
  if not 'user_id' in session:
    return redirect('/login')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute("""
    DELETE FROM todos WHERE id = ?
  """,(id,))
  conn.commit()
  conn.close()
  return redirect('/')

@app.route('/complete/<id>', )
def complete(id):
  if not 'user_id' in session:
    return redirect('/login')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'UPDATE todos SET complete = 1 WHERE id = ?',(id,))
  conn.commit()
  conn.close()
  return redirect('/')

@app.route('/update/<id>', methods=['POST'])
def update(id):
  if not 'user_id' in session:
    return redirect('/login')
    
  title = request.form.get('title')
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'UPDATE todos SET title = ? WHERE id = ?',(title, id,))
  conn.commit()
  conn.close()
  return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  
  email = request.form.get('email')
  password = request.form.get('password')
  
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'SELECT * FROM users WHERE email = ?', (email,))
  user = cursor.fetchone()
  conn.close()

  if not user or not check_password_hash(user[3], password):
    return redirect('/login')

  session['user_id'] = user[0]

  return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'GET':
    return render_template('signup.html')

  name = request.form.get('name')
  email = request.form.get('email')
  password = request.form.get('password')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'SELECT * FROM users WHERE email = ?', (email,))
  user = cursor.fetchone()

  if user:
    return redirect('/signup')

  cursor.execute(
    'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
    (name, email, generate_password_hash(password, method='sha256'))
  )
  
  conn.commit()
  conn.close()

  return redirect('/login')

@app.route('/logout')
def logout():
  if 'user_id' in session:
    session.pop('user_id', None)

  return redirect('/');


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)