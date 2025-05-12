from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        message TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'spark' and password == 'spark001':  # Set your admin credentials here
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    department = request.form['department']
    message = request.form['message']
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (name, email, department, message) VALUES (?, ?, ?, ?)', (name, email, department, message))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    valid_sort_fields = ['id', 'name', 'department', 'year_of_study']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'
    if order not in ['asc', 'desc']:
        order = 'asc'
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM feedback ORDER BY {sort_by} {order.upper()}')
    feedbacks = c.fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks, sort_by=sort_by, order=order)

@app.route('/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
