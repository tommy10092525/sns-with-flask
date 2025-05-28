from flask import Flask, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_required,login_user,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy
import uuid 
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

from models import User, Post, Reaction, Friend, Class, Class_entry, db

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.db"
app.config["SECRET_KEY"]="codemates1234567890"
db.init_app(app)

login_manager=LoginManager(app)
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    """ユーザーをロードする関数"""
    return User.query.filter(User.id==user_id).first()

@app.route("/")
def index():
    """トップページにリダイレクトする関数"""
    return redirect(url_for("home"))

@app.route("/home")
def home():
    """ホームページを表示する関数"""
    posts= Post.query.join(User).add_columns(User.username).all()
    return render_template("home.html", posts=posts)

@app.route("/create", methods=["POST","GET"])
@login_required
def create():
    """投稿を作成する関数"""
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
    """投稿を表示する関数"""
    post_id=str(post_id)
    post=Post.query.filter(Post.id==post_id).first()
    user=User.query.filter(User.id==post.user_id).first()
    return render_template("post.html", post=post.to_dict(), user=user.to_dict())

@app.route("/post/<uuid:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    """投稿を削除する関数"""
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
    """ログインページを表示する関数"""
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
    """ログアウトする関数"""
    logout_user()
    session.clear()
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    """新規登録ページを表示する関数"""
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        department=request.form.get("department")
        password=generate_password_hash(request.form.get("password"),method="pbkdf2:sha256")
        user=User.query.filter(User.username==username).first()
        if user:
            return redirect(url_for("signup"))
        db.session.add(User(username=username, email=email, password=password, department=department))
        db.session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("signup.html")

@app.route("/friend", methods=["POST","GET"])
@login_required
def friend():
    """フレンドページを表示する関数"""
    friends=Friend.query.filter(Friend.user_id==current_user.id).all()
    friends_list=[]
    for friend in friends:
        friend_user=User.query.filter(User.id==friend.friend_id).first()
        friend_user_dict=friend_user.to_dict()
        friend_user_dict["friend_id"]=friend.friend_id
        friend_user_dict["user_id"]=friend.user_id
        friend_user_dict["created_at"]=friend.created_at.strftime("%Y-%m-%d %H:%M:%S")  
        friends_list.append(friend_user_dict)
    return render_template("friend.html", friends=friends_list)

@app.route("/friend/<uuid:friend_id>", methods=["POST"])
@login_required
def friend_add(friend_id):
    """フレンドを追加する関数"""
    friend_id=str(friend_id)
    db.session.add(Friend(user_id=current_user.id, friend_id=friend_id))
    db.session.commit()
    return redirect(url_for("user", user_id=friend_id))

@app.route("/friend/<uuid:friend_id>/delete", methods=["POST"])
@login_required
def friend_delete(friend_id):
    """フレンドを削除する関数"""
    friend_id=str(friend_id)
    db.session.delete(Friend.query.filter(Friend.user_id==current_user.id, Friend.friend_id==friend_id).first())
    db.session.commit()
    return redirect(url_for("user", user_id=friend_id))

@app.route("/schedule")
@login_required
def schedule():
    """時間割ページを表示する関数"""
    classes=Class_entry.query.filter(Class_entry.user_id==current_user.id).all()
    classes_list=[]
    user=User.query.filter(User.id==current_user.id).first()
    for class_entry in classes:
        class_detail=Class.query.filter(Class.id==class_entry.class_id).first()
        class_detail_dict=class_detail.to_dict()
        classes_list.append(class_detail_dict)
    classes_list.sort(key=lambda x: x["time"])
    return render_template("schedule.html", classes=classes_list, user=user.to_dict())

@app.route("/user/<uuid:user_id>")
@login_required
def user(user_id):
    """ユーザーページを表示する関数"""
    user_id=str(user_id)
    user=User.query.filter(User.id==user_id).first()
    friend=Friend.query.filter(Friend.user_id==current_user.id, Friend.friend_id==user_id).first()
    if not user:
        return redirect(url_for("home"))
    posts=Post.query.filter(Post.user_id==str(user_id)).all()
    return render_template("user.html", user=user.to_dict(), posts=list(map(lambda x: x.to_dict(), posts)), friend=friend)

@app.route("/classes")
def classes():
    name=request.args.get("name")
    code=request.args.get("code")
    department=request.args.get("department")
    time=request.args.get("time")
    day=request.args.get("day")
    season=request.args.get("season")
    teacher=request.args.get("teacher")
    filters=[]
    if season=="spring":
        filters.append(Class.is_spring==True)
    elif season=="autumn":
        filters.append(Class.is_autumn==True)
    elif season=="other":
        filters.append(Class.is_spring==False)
        filters.append(Class.is_autumn==False)
    if name:
        filters.append(Class.name.like(f"%{name}%"))
    if code:
        filters.append(Class.code.like(f"%{code}%"))
    if department:
        filters.append(Class.department==department)
    if time:
        filters.append(Class.time==time)
    if day: 
        filters.append(Class.day==day)
    if teacher:
        filters.append(Class.teacher.like(f"%{teacher}%"))
    classes=Class.query.filter(*filters).limit(1000).all()
    return render_template("classes.html", classes=list(map(lambda x: x.to_dict(), classes)))

@app.route("/class/<uuid:class_id>")
def class_detail(class_id):
    """授業詳細ページを表示する関数"""
    class_id=str(class_id)
    class_detail=Class.query.filter(Class.id==class_id).first()
    class_entry=Class_entry.query.filter(Class_entry.class_id==class_id,Class_entry.user_id==current_user.id).first()
    return render_template("class_detail.html", class_detail=class_detail.to_dict(),class_entry=class_entry)

@app.route("/class/<uuid:class_id>/add", methods=["GET"])
@login_required
def class_add(class_id):
    """授業を時間割に追加する関数"""
    class_id=str(class_id)
    db.session.add(Class_entry(user_id=current_user.id, class_id=class_id))
    db.session.commit()
    return redirect(url_for("schedule"))

@app.route("/class/<uuid:class_id>/delete",methods=["GET"])
@login_required
def class_delete(class_id):
    """授業を時間割から削除する関数"""
    class_id=str(class_id)
    class_entry=Class_entry.query.filter(Class_entry.class_id==class_id,Class_entry.user_id==current_user.id).first()
    db.session.delete(class_entry)
    db.session.commit()
    return redirect(url_for("schedule"))

@app.route("/aboutme", methods=["POST","GET"])
@login_required
def aboutme():
    """アバウトミーのページを表示する関数"""
    if request.method=="POST":
        name=request.form.get("name")
        department=request.form.get("department")
        user=User.query.filter(User.id==current_user.id).first()
        user.name=name
        user.department=department
        db.session.commit()
        return redirect(url_for("aboutme"))
    else:
        user=User.query.filter(User.id==current_user.id).first()
        return render_template("aboutme.html", user=user.to_dict())

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)