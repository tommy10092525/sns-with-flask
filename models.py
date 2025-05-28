
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
db=SQLAlchemy()


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
    department=db.Column(db.String)
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "department": self.department
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
    """学部"""
    department=db.Column(db.String, nullable=False)
    """年"""
    year=db.Column(db.Integer, nullable=False)
    """授業コード"""
    code=db.Column(db.String, nullable=False)
    """科目名"""
    name=db.Column(db.String, nullable=False)
    """開講時期"""
    season=db.Column(db.String, nullable=False)
    """時限"""
    time=db.Column(db.Integer, nullable=False)
    """曜日"""
    day=db.Column(db.String, nullable=False)
    """教室名称"""
    place=db.Column(db.String, nullable=False)
    """単位"""
    unit=db.Column(db.Integer, nullable=False)
    """シラバスURL"""
    url=db.Column(db.String, nullable=False)
    """講師"""
    teacher=db.Column(db.String, nullable=False)
    """配当年次_最小"""
    grade_min=db.Column(db.Integer, nullable=False)
    """配当年次_最大"""
    grade_max=db.Column(db.Integer, nullable=False)
    """備考"""
    note=db.Column(db.String, nullable=False)
    """エラー"""
    error=db.Column(db.String, nullable=False)
    """春学期かどうか"""
    is_spring=db.Column(db.Boolean, nullable=False)
    """秋学期かどうか"""
    is_autumn=db.Column(db.Boolean, nullable=False)
    def to_dict(self):
        return {
            "id": self.id,
            "department": self.department,
            "year": self.year,
            "code": self.code,
            "name": self.name,
            "season": self.season,
            "time": self.time,
            "day": self.day,
            "place": self.place,
            "unit": self.unit,
            "url": self.url,
            "teacher": self.teacher,
            "grade_min": self.grade_min,
            "grade_max": self.grade_max,
            "note": self.note,
            "error": self.error,
            "is_spring": self.is_spring,
            "is_autumn": self.is_autumn
        }
    def __init__(self,department,year,code,name,season,time,day,place,unit,url,teacher,grade_min,grade_max,note,error):
        self.department=department
        self.year=year
        self.code=code
        self.name=name
        self.season=season
        self.time=time
        self.day=day
        self.place=place
        self.unit=unit
        self.url=url
        self.teacher=teacher
        self.grade_min=grade_min
        self.grade_max=grade_max
        self.note=note
        self.error=error
        if season in ["年間授業/Yearly","春学期・秋学期/Spring・Fall"]:
            self.is_spring=True
            self.is_autumn=True
        elif season in ["春学期授業/Spring"]:
            self.is_spring=True
            self.is_autumn=False
        elif season in ["秋学期授業/Fall"]:
            self.is_spring=False
            self.is_autumn=True
        else:
            self.is_spring=False
            self.is_autumn=False

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
    
