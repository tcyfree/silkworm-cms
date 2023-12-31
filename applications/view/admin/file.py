import os
from flask import Blueprint, request, render_template, jsonify, current_app, make_response

from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.rights import authorize
from applications.extensions import db
from applications.models import Photo
from applications.common.utils import upload as upload_curd
from applications.AIDetector_pytorch import Detector
from applications.common import curd
from applications.common.utils.validate import str_escape

# compatible mini and web terminals
admin_file = Blueprint('adminFile', __name__, url_prefix='/')


#  图片管理
@admin_file.get('/')
@authorize("admin:file:main")
def index():
    return render_template('admin/photo/photo.html')


#  图片数据
@admin_file.get('/table')
@authorize("admin:file:main")
def table():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    data, count = upload_curd.get_photo(page=page, limit=limit)
    return table_api(data=data, count=count)


#   上传
@admin_file.get('/upload')
@authorize("admin:file:add", log=True)
def upload():
    return render_template('admin/photo/photo_add.html')


#   上传接口
@admin_file.post('/upload')
# @authorize("admin:file:add", log=True)
def upload_api():
    model = current_app.model 
    if 'file' in request.files:
        photo = request.files['file']
        print(photo)
        mime = request.files['file'].content_type
        age = request.args.get('age', 0)
        address = request.args.get('address', '')
        remark = request.args.get('remark', '')
        file_url = upload_curd.upload_one(photo, mime, photo.filename)
        pid, image_info = upload_curd.upload_two(model, photo.filename, age, address, remark)

        serve_url = 'http://cxy.ssdlab.cn/'
        res = {
            "msg": "上传成功",
            "code": 0,
            "success": True,
            "status":1,
            "src": file_url,
            # 'image_url': 'http://localhost:5003/static/upload/' + pid,
            # 'draw_url': 'http://localhost:5003/static/tmp/comp/' + pid,
            'image_url': serve_url + 'static/upload/' + pid,
            'draw_url': serve_url + 'static/tmp/comp/' + pid,
            'image_info': image_info
        }
        return jsonify(res)
    return fail_api()


# # show photo
# @admin_file.get('/show/<path:file>')
# # @authorize("admin:file:show", log=True)
# def show_photo(file):
#     if request.method == 'GET':
#         if not file is None:
#             image_data = open(f'static/tmp/comp/{file}', "rb").read()
#             response = make_response(image_data)
#             response.headers['Content-Type'] = 'image/png'
#             return response


#    图片删除
@admin_file.route('/delete', methods=['GET', 'POST'])
@authorize("admin:file:delete", log=True)
def delete():
    _id = request.form.get('id')
    res = upload_curd.delete_photo_by_id(_id)
    if res:
        return success_api(msg="删除成功")
    else:
        return fail_api(msg="删除失败")


# 图片批量删除
@admin_file.route('/batchRemove', methods=['GET', 'POST'])
@authorize("admin:file:delete", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')
    photo_name = Photo.query.filter(Photo.id.in_(ids)).all()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    for p in photo_name:
        os.remove(upload_url + '/' + p.name)
    photo = Photo.query.filter(Photo.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    if photo:
        return success_api(msg="删除成功")
    else:
        return fail_api(msg="删除失败")

#  编辑用户
@admin_file.get('/edit/<int:id>')
@authorize("admin:file:edit", log=True)
def edit(id):
    photo = curd.get_one_by_id(Photo, id)
    
    return render_template('admin/photo/edit.html', photo=photo)


#  编辑用户
@admin_file.put('/update')
@authorize("admin:file:edit", log=True)
def update():
    req_json = request.get_json(force=True)
    id = str_escape(req_json.get("userId"))
    reply = str_escape(req_json.get('reply'))
    Photo.query.filter_by(id=id).update({'reply': reply})

    db.session.commit()
    return success_api(msg="更新成功")