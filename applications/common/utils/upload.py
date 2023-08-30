import os
from flask import current_app
from sqlalchemy import desc
from applications.extensions import db
from applications.extensions.init_upload import photos
from applications.models import Photo
from applications.schemas import PhotoOutSchema
from applications.common.curd import model_to_dicts

from applications.core.main import c_main as dispose
from PIL import Image

def get_photo(page, limit):
    photo = Photo.query.order_by(desc(Photo.create_time)).paginate(page=page, per_page=limit, error_out=False)
    count = Photo.query.count()
    data = model_to_dicts(schema=PhotoOutSchema, data=photo.items)
    return data, count


def upload_one(photo, mime, filename):
    file_url = '/_uploads/photos/'+filename
    # file_url = photos.url(filename)
    upload_url = os.path.join(current_app.config.get("UPLOADED_PHOTOS_DEST"), filename)
    photo.save(upload_url)
    return file_url


def upload_two(model, filename, age):
    str(0 if age is None else age)
    upload_url = os.path.join(current_app.config.get("UPLOADED_PHOTOS_DEST"), filename)
    pid, image_info = dispose(upload_url, model, filename.rsplit('.', 1)[-1], age)

    photo = Photo(name=filename, href='/static/tmp/comp/' + pid, mime='', size=0)
    db.session.add(photo)
    db.session.commit()

    return pid, image_info


def delete_photo_by_id(_id):
    photo_name = Photo.query.filter_by(id=_id).first().name
    photo = Photo.query.filter_by(id=_id).delete()
    db.session.commit()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    os.remove(upload_url + '/' + photo_name)
    return photo
