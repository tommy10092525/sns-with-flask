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
    
class Reaction(db.Model):
    __tablename__="reactions"
    id=db.Column(db.String, primary_key=True, default=lambda x: str(uuid.uuid4()))
    post_id=db.Column(db.String, db.ForeignKey("posts.id"), nullable=False)
    user_id=db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    reaction=db.Column(db.String, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now)
    def to_dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "reaction": self.reaction,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Friend(db.Model):
    __tablename__="friends"
    id=db.Column(db.String, primary_key=True, default=lambda x: str(uuid.uuid4()))
    user_id=db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    friend_id=db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now)
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_id": self.friend_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Class(db.Model):
    __tablename__="classes"
    id=db.Column(db.String, primary_key=True, default=lambda x: str(uuid.uuid4()))
    department=db.Column(db.String, nullable=False)
    name=db.Column(db.String, nullable=False)
    season=db.Column(db.String, nullable=False)
    teacher=db.Column(db.String, nullable=False)
    place=db.Column(db.String, nullable=False)
    unit=db.Column(db.Integer, nullable=False)
    url=db.Column(db.String, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now)
    def to_dict(self):
        return {
            "id": self.id,
            "department": self.department,
            "name": self.name,
            "season": self.season,
            "teacher": self.teacher,
            "place": self.place,
            "unit": self.unit,
            "url": self.url,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Class_entry(db.Model):
    __tablename__="class_entries"
    id=db.Column(db.String, primary_key=True, default=lambda x: str(uuid.uuid4()))
    class_id=db.Column(db.String, db.ForeignKey("classes.id"), nullable=False)
    user_id=db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now)
    def to_dict(self):
        return {
            "id": self.id,
            "class_id": self.class_id,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    


login_manager=LoginManager(app)
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id==user_id).first()

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    posts= Post.query.join(User).add_columns(User.username).all()
    return render_template("home.html", posts=posts)

@login_required
@app.route("/create", methods=["POST","GET"])
def create():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if request.method=="POST":
        title=request.form.get("title")
        content=request.form.get("content")
        ip=request.remote_addr
        user_id=current_user.id
        db.session.add(Post(title=title, content=content, ip=ip, user_id=user_id))
        db.session.commit()
        return redirect(url_for("home"))
    else:
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
    if request.method=="POST":
        post_id=str(post_id)
        post=Post.query.filter(Post.id==post_id).first()
        if post.user_id!=current_user.id:
            return redirect(url_for("home"))
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        user=User.query.filter(User.username==username).first()
        if user and user.check_password(password):
            login_user(user)
            session["user_id"]=user.id
            return redirect(url_for("home"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        password=generate_password_hash(request.form.get("password"),method="pbkdf2:sha256")
        user=User.query.filter(User.username==username or User.email==email).first()
        if user:
            return redirect(url_for("signup"))
        db.session.add(User(username=username, email=email, password=password))
        db.session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("signup.html")

@app.route("/friend")
def friend():
    return render_template("friend.html")

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)