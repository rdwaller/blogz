from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pal1d0@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(125))
    body = db.Column(db.String(2500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST', 'GET'])
def create_post():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if blog_body == '' or blog_title == '':
            return render_template('create_post.html', title="Build a Blog!")

        blog_entry = Blog(blog_title, blog_body)
        db.session.add(blog_entry)
        db.session.commit()

        post_id = str(blog_entry.id)

        return redirect('/view_post?id=' + post_id)

    else:        
        return render_template('create_post.html', title="Build a Blog!")

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    blogs = Blog.query.all()

    return render_template('blog.html',title="Build a Blog!", blogs=blogs)

@app.route('/view_post', methods=['POST', 'GET'])
 
def show_post():
    post_id = int(request.args.get('id'))
    post = Blog.query.get(post_id)

    return render_template('view_post.html', title="Build a Blog!", post=post)

if __name__ == '__main__':
  app.run()