from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pal1d0@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class User(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(120), unique=True)
  password = db.Column(db.String(120))
  blogs = db.relationship('Blog', backref='user')

  def __init__(self, username, password):
    self.username = username
    self.password = password
#   self.blogs = blogs

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(125))
    body = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
      session['user'] = user
      return redirect('/newpost')
    elif user and user.password != password:
      return redirect('login.html')
    else:
      return redirect('/login.html')

  return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['enter_username']
        password = request.form['enter_password']
        verify_password = request.form['verify_password']
        email = request.form['enter_email']
        existing_user = User.query.filter_by(username=username).first()
        
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
    #        session['user'] = user
            return redirect('/')
        else: 
            return redirect('/signup?username={0}&email={1}&username_error={2}&password_error={3}&verify_password_error={4}&email_error={5}'.format(username, email, username_error, password_error, verify_password_error, email_error))
    else:
        return render_template('signup.html', username=request.args.get('username'), email=request.args.get('email'), username_error = request.args.get('username_error'), password_error=request.args.get('password_error'), verify_password_error=request.args.get('verify_password_error'))

@app.route('/newpost', methods=['POST', 'GET'])
def create_post():

    #added 'blog_user' request and attribute below, but did not update any forms.

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        blog_user = request.form['blog_user']

        if blog_body == '' or blog_title == '':
            return render_template('create_post.html', title="Blogz!")

        blog_entry = Blog(blog_title, blog_body, blog_user)
        db.session.add(blog_entry)
        db.session.commit()

        post_id = str(blog_entry.id)

        return redirect('/view_post?id=' + post_id)

    else:        
        return render_template('create_post.html', title="Blogz!")

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    blogs = Blog.query.all()

    return render_template('blog.html',title="Bloz!", blogs=blogs)

@app.route('/view_post', methods=['POST', 'GET'])
 
def show_post():
    post_id = int(request.args.get('id'))
    post = Blog.query.get(post_id)

    return render_template('view_post.html', title="Blogz!", post=post)

if __name__ == '__main__':
  app.run()