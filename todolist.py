import sqlite3
from flask import Flask, request,  url_for, redirect, g, flash, session, render_template, abort

DATABASE = 'lab5.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def welcome():
    return '<h1>This is Lab 5!</h1>'

@app.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        description = request.form['description']
        priority = request.form['priority']
        category = request.form['category']
        addTask(category, description, priority)
        flash('New task was successfully posted')
        return redirect(url_for('task'))
    return render_template('show_entries.html', tasks=query_db('SELECT * FROM tasks'))

@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    description = request.form['description']
    priority = request.form['priority']
    category = request.form['category']
    removeTask(category, description, priority)
    flash('Task was successfully deleted')
    return redirect(url_for('task'))

@app.route('/edit/<selectId>', methods=['GET','POST'])
def edit():
    if not session.get('logged_in'):
        abort(401)
    if request.method =='POST':
        description = request.form['description']
        priority = request.form['priority']
        category = request.form['category']
        editTask(selectId,category, description, priority)
        flash('Task was successfully updated')
        return redirect(url_for('task'))
    return render_template('edit.html', tasks=query_db('SELECT * FROM tasks WHERE id = ?', [selectId], one=True))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('Invalid username', 'error')
        elif request.form['password'] != app.config['PASSWORD']:
            flash('Invalid password', 'error')
        else:
            session['logged_in'] = True
            return redirect(url_for('task'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('task'))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query,args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def addTask(category, description, priority):
    query_db('INSERT INTO tasks (category, description, priority) values (?, ?, ?)',[category, description, int(priority)], one=True)
    get_db().commit()

def removeTask(category, description, priority):
    query_db('DELETE FROM tasks where category = ? and description = ? and priority = ?',[category, description, int(priority)], one=True)
    get_db().commit()
def editTask(selectId, category, description, priority):
    query_db('UPDATE tasks set category = ? and description = ? and priority = ? WHERE id = ?', [category, description, int(priority), int(selectId)], one=True)

if __name__ == '__main__':
    #query_db('CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, description VARCHAR, category VARCHAR, priority INT)')
    app.debug = True
    app.run()
