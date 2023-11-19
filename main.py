from flask import Flask, request, render_template, flash, redirect, session, url_for
import pickledb
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = '12022008'

db = pickledb.load('base.db', True)

if not db.exists('users'):
    db.set('users', [])
    db.set('counter_user_id', 0)
    db.dump()

if not db.get('counter_post_id'):
    db.set('counter_post_id', 1)
    db.dump()


def next_post_id():
    counter = db.get('counter_post_id')
    db.set('counter_post_id', counter + 1)
    db.dump()
    return counter


def next_user_id():
    counter = db.get('counter_user_id')
    db.set('counter_user_id', counter + 1)
    db.dump()
    return counter


def set_info(title, text, username):
    post_id = next_post_id()
    now = datetime.now()
    username = username
    formatted_now = now.strftime("%Y-%m-%d %H:%M")
    db.set(str(post_id), {"title": title, "text": text, "time": str(formatted_now), "username": username})
    db.dump()


@app.route('/user/<username>')
def user(username):
    for user in db.get('users'):
        if user.get('username') == username:
            return render_template('user.html', username=username)
    return "User not found"

@app.route('/')
def home():
    if session.get('isLogged'):
        posts = []
        for post_id in range(db.get('counter_post_id') - 1, 0, -1):
            post = db.get(str(post_id))
            if post:
                posts.append(post)
        return render_template("all_posts.html", posts=posts)
    else:
        return render_template('home_welcome.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        users_list = db.get('users')
        this_user = None
        for user in users_list:
            if request.form['username'] == user['username']:
                this_user = user
                if request.form['password'] == this_user['password']:
                    session['username'] = request.form['username']
                    session['isLogged'] = True
                    print(session['username'])
                    return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session['isLogged'] = False
    session.clear()
    return redirect(url_for('home'))


@app.route('/post')
def post():
    if session.get('isLogged'):
        return render_template('make_post.html')
    else:
        return redirect(url_for('home'))


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == "POST":
        users = db.get('users')
        users.append({'id': next_user_id(), 'username': request.form['username'], 'password': request.form['password']})
        db.set('users', users)
        db.dump()
        session['isLogged'] = True
        session['username'] = request.form['username']
        return redirect('/')

    return render_template("reg.html")


@app.route("/create_post", methods=["POST"])
def create_post():
    if request.method == "POST":
        post_title = request.form['postTitle']
        post_text = request.form['postText']
        user_username = session.get('username')
        set_info(post_title, post_text, user_username)

        # Добавляем сообщение о публикации поста в объект запроса
        flash('Beitrag veröffentlicht!', 'success')

        return redirect(url_for('home'))


app.run(debug=True)
