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

if not db.exists('users_reviews'):
    db.set('users_reviews', {})
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


now = datetime.now()
formatted_now = now.strftime("%Y-%m-%d %H:%M")


def set_info(title, text, username):
    post_id = next_post_id()
    now = datetime.now()
    username = username
    formatted_now = now.strftime("%Y-%m-%d %H:%M")
    db.set(str(post_id), {"title": title, "text": text, "time": str(formatted_now), "username": username})
    db.dump()


@app.route('/user/<username>')
def user(username):
    all_reviews = db.get('users_reviews').get(username, [])
    print(all_reviews)

    if username != session.get('username'):
        for user in db.get('users'):
            if user.get('username') == username:
                return render_template('user.html', username=username, reviews=all_reviews)
        return "User not found"
    else:
        return render_template('my_user_page.html', reviews=all_reviews)


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
        input_username = request.form['username']

        # Проверка существования пользователя
        if any(user.get('username') == input_username for user in users_list):
            # Поиск пользователя с введенным именем
            this_user = next((user for user in users_list if user['username'] == input_username), None)

            # Проверка пароля
            if this_user and request.form['password'] == this_user['password']:
                session['username'] = input_username
                session['isLogged'] = True
                print(session['username'])
                return redirect(url_for('home'))
            else:
                flash('Incorrect password or username', 'error')
                return render_template('login.html')
        else:
            flash('User does not exist', 'error')
            return render_template('login.html')
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
        # Check if the username is already taken
        if 'username' in request.form and any(user.get('username') == request.form['username'] for user in users):
            flash('Username is already taken. Please choose a different username.', 'error')
            return redirect('/reg')  # Redirect to registration page with flash message

        else:
            users.append(
                {'id': next_user_id(), 'username': request.form['username'], 'password': request.form['password']})
            db.set('users', users)
            db.dump()
            session['isLogged'] = True
            session['username'] = request.form['username']
            return redirect('/')
    else:
        return render_template('reg.html')


@app.route("/create_post", methods=["POST"])
def create_post():
    if request.method == "POST":
        post_title = request.form['postTitle']
        post_text = request.form['postText']
        user_username = session.get('username')

        if post_title:  # Проверка, что и заголовок, и текст существуют
            set_info(post_title, post_text, user_username)
            flash('Beitrag veröffentlicht!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Post title and text are required.', 'error')
            return render_template('make_post.html')

@app.route('/user_review', methods=['POST'])
def user_review():
    users_reviews = db.get('users_reviews')

    author = session.get('username')
    username = request.form['username']
    title = request.form['title']
    text = request.form['text']
    show_author = show_author = request.form.get('show_author', False) == 'true'
    found = False



    for k in users_reviews:
        if k == username:
            users_reviews[username].append({'title': title, 'text': text, 'author': author, 'likes': 0, 'dislikes': 0,
                                            'is_author_visible': show_author, 'time': formatted_now})
            found = True
            break

    if not found:
        users_reviews[username] = [{'title': title, 'text': text, 'author': author, 'likes': 0, 'dislikes': 0,
                                    'is_author_visible': show_author, 'time': formatted_now}]

    db.set('users_reviews', users_reviews)

    return redirect(url_for('user', username=username))


app.run(debug=True)
