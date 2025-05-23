from flask import Flask, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_required,login_user,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy
import uuid 
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.db"
app.config["SECRET_KEY"]="aaaaaaa"

db=SQLAlchemy(app)

class Post(db.Model):
    __tablename__="posts"
    id=db.Column(db.String, primary_key=True, default=lambda x: str(uuid.uuid4()))
    title=db.Column(db.String, nullable=False)
    content=db.Column(db.String, nullable=False)
    ip=db.Column(db.String, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now)
    user_id=db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    def to_dict(self):
        if len(self.content)>100:
            content=self.content[:100]+"..."
        else:
            content=self.content
        return {
            "id": self.id,
            "title": self.title,
            "content": content,
            "ip": self.ip,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id
        }

class User(db.Model,UserMixin):
    __tablename__="users"
    id=db.Column(db.String, primary_key=True, default=lambda x: str(uuid.uuid4()))
    username=db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False)
    password=db.Column(db.String, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now)
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def get_id(self):
        return str(self.id)

login_manager=LoginManager(app)
login_manager.init_app(app)
login_manager.login_view="login_get"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id==user_id).first()



@app.route("/")
def index():
    posts= Post.query.join(User).add_columns(User.username).all()
    print(posts)
    return render_template("index.html", posts=posts)

@login_required
@app.route("/create", methods=["POST"])
def create():
    title=request.form.get("title")
    content=request.form.get("content")
    ip=request.remote_addr
    user_id=current_user.id
    db.session.add(Post(title=title, content=content, ip=ip, user_id=user_id))
    db.session.commit()
    return redirect(url_for("index"))

@login_required
@app.route("/create",methods=["GET"])
def create_get():
    return render_template("create.html")

@app.route("/post/<uuid:post_id>")
def post(post_id):
    post_id=str(post_id)
    post=Post.query.filter(Post.id==post_id).first()
    user=User.query.filter(User.id==post.user_id).first()
    return render_template("post.html", post=post.to_dict(), user=user.to_dict())

@login_required
@app.route("/post/<uuid:post_id>/delete", methods=["POST"])
def delete(post_id):
    post_id=str(post_id)
    post=Post.query.filter(Post.id==post_id).first()
    if post.user_id!=current_user.id:
        return redirect(url_for("index"))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username=request.form.get("username")
    password=request.form.get("password")
    user=User.query.filter(User.username==username).first()
    print(username,password)
    print(user)
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login_get"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET"])
def signup_get():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup_post():
    username=request.form.get("username")
    email=request.form.get("email")
    password=generate_password_hash(request.form.get("password"),method="pbkdf2:sha256")
    user=User.query.filter(User.username==username or User.email==email).first()
    if user:
        return redirect(url_for("signup_get"))
    db.session.add(User(username=username, email=email, password=password))
    db.session.commit()
    return redirect(url_for("login_get"))

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)