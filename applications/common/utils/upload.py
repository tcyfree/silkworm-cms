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
    # Open image and compress and save
    img = Image.open(photo)
    img.thumbnail((400, 400))  # Adjust your size
    upload_compress_url = os.path.join(current_app.config.get("UPLOADED_PHOTOS_DEST"), filename)
    img.save(upload_compress_url, quality=85)

    size = os.path.getsize(upload_compress_url)
    print('compress-size: ', size)
    photo = Photo(name=filename, href=file_url, mime=mime, size=size)
    db.session.add(photo)
    db.session.commit()
    return file_url


def upload_two(model, filename, age):
    str(0 if age is None else age)
    upload_url = os.path.join(current_app.config.get("UPLOADED_PHOTOS_DEST"), filename)
    pid, image_info = dispose(upload_url, model, filename.rsplit('.', 1)[-1], age)
    return pid, image_info


def delete_photo_by_id(_id):
    photo_name = Photo.query.filter_by(id=_id).first().name
    photo = Photo.query.filter_by(id=_id).delete()
    db.session.commit()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    os.remove(upload_url + '/' + photo_name)
    return photo
