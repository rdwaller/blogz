from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pal1d0@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class User(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(120), unique=True)
  password = db.Column(db.String(120))
  blogs = db.relationship('Blog', backref='user')

  def __init__(self, username, password):
    self.username = username
    self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(125))
    body = db.Column(db.String(2500))
    username = db.Column(db.String(120), db.ForeignKey('user.username'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

@app.before_request
def require_login():
    allowed_routes = ['index', 'list_blogs', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist.')
            return redirect('/login')
        elif user and user.password == password:
            session['user'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Incorrect password.')
            return redirect('/login')
    else:
        return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['user']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['enter_username']
        password = request.form['enter_password']
        verify_password = request.form['verify_password']
        email = request.form['enter_email']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            def validate_username(username):
                if username == '':
                    return False
                elif len(username) < 3 or len(username) > 20:
                    return False
                elif (' ' in username) == True:
                    return False
                else:
                    return True

            def validate_password(password):
                if password == '':
                    return False
                elif len(password) < 3 or len(password) > 20:
                    return False
                else:
                    return True

            def validate_email(email):
                if len(email) == 1 or len(email) ==2 or len(email) > 20:
                    return False
                elif (' ' in email) == True:
                    return False
                elif ('@' in email) < 1 or ('@' in email) > 1:
                    return False
                elif ('.' in email) < 1 or ('.' in email) > 1:
                    return False
                else:
                    return True

            def password_match(verify_password, password):
                if verify_password != password:
                    return False
                else:
                    return True
            
            if validate_username(username) == False:
                username_error = 'That is not a valid username.'
            else:
                username_error = ''

            if validate_password(password) == False:
                password_error = 'That is not a valid password.'
            else:
                password_error = ''   

            if password_match(verify_password, password) == False:
                verify_password_error = 'Passwords do not match.'
            else:
                verify_password_error = ''

            if validate_email(email) == True or email == '':
                email_error = ''
            else:
                email_error = 'That is not a valid email address.'
        
            if validate_username(username) == True and validate_password(password) == True and password_match(verify_password, password)==True and (validate_email(email) == True or email == ''):
                user = User(username, password)
                db.session.add(user)
                db.session.commit()
                session['user'] = username
                return redirect('/newpost')
            else: 
                return redirect('/signup?username={0}&email={1}&username_error={2}&password_error={3}&verify_password_error={4}&email_error={5}'.format(username, email, username_error, password_error, verify_password_error, email_error))
        else:
            flash('Username already exists.')
            return redirect('/signup')
    else:
        if request.args.get('username') == None:
            username = ''
        else:
            username = request.args.get('username')
        if request.args.get('email') == None:
            email = ''
        else:
            email = request.args.get('email')

        return render_template('signup.html', username=username, email=email, username_error = request.args.get('username_error'), password_error=request.args.get('password_error'), verify_password_error=request.args.get('verify_password_error'), email_error=request.args.get('email_error'))
        

@app.route('/newpost', methods=['POST', 'GET'])
def create_post():
    user = User.query.filter_by(username=session['user']).first()
    if request.method == 'POST':
        title = request.form['blog_title']
        body = request.form['blog_body']
        if body == '' or title == '':
            return render_template('newpost.html', title="Blogz!")
        else:
            pass
        blog_entry = Blog(title, body, user)
        db.session.add(blog_entry)
        db.session.commit()
        post_id = str(blog_entry.id)
        return redirect('/view_post?id=' + post_id)
    else:        
        return render_template('newpost.html', title="Blogz!")

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    blogs = Blog.query.all()
    username = request.args.get('username')
    user_blogs = Blog.query.filter_by(username=username).all()

    return render_template('blog.html',title="Blogz!", blogs=blogs, username=username, user_blogs=user_blogs)

@app.route('/view_post', methods=['POST', 'GET'])
 
def show_post():
    post_id = int(request.args.get('id'))
    post = Blog.query.get(post_id)

    return render_template('view_post.html', title="Blogz!", post=post)

@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', title="Blogz!", users=users)

if __name__ == '__main__':
  app.run()