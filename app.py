import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Initialize a connection count
connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection_count += 1
    connection.row_factory = sqlite3.Row
    return connection

def close_db_connection(cursor):
    global connection_count
    if cursor:
        cursor.close()
        connection_count -= 1

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    close_db_connection(connection)
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    close_db_connection(connection)
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.warning('Non-existing article accessed: %d', post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "%s" retrieved!', post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            close_db_connection(connection)
            app.logger.info('New article created: "%s"', title)
            return redirect(url_for('index'))
    return render_template('create.html')

# A /health endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Health successfully retrieved!')
    return response

# A /metrics endpoint
@app.route('/metrics')
def metrics():
    global connection_count
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    response = app.response_class(
            response=json.dumps({"db_connection_count": connection_count, "post_count": len(posts)}),
            status=200,
            mimetype='application/json'
    )
    close_db_connection(connection)
    return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',
                       format='%(levelname)s:%(name)s:%(message)s',
                       level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
