from app import app,db
with app.app_context():
    db.create_all()
    db.session.commit()
    print("テーブルが作成されました")