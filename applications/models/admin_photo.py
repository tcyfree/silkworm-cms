import datetime
from applications.extensions import db


class Photo(db.Model):
    __tablename__ = 'admin_photo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    href = db.Column(db.String(255))
    address = db.Column(db.String(128))
    remark = db.Column(db.String(128))
    reply = db.Column(db.String(128))
    mime = db.Column(db.String(512))
    size = db.Column(db.String(30))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)