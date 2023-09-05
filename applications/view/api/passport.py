from flask import Blueprint, session, request, jsonify
from flask_login import current_user, login_user, logout_user

from applications.common.admin_log import login_log
from applications.common.utils.http import fail_api, success_api
from applications.models import User
from applications.common.utils.validate import str_escape
from applications.extensions import db

bp = Blueprint('passport', __name__, url_prefix='/passport')


# 登录
@bp.post('/login')
def login_post():
    req_json = request.get_json(force=True)
    username = str_escape(req_json.get("username"))
    password = str_escape(req_json.get("password"))
    if not username or not password:
        return fail_api(msg="用户名或密码没有输入!")

    user = User.query.filter_by(username=username).first()

    if not user:
        return fail_api(msg="不存在的用户")

    if user.enable == 0:
        return fail_api(msg="用户被暂停使用")

    if username == user.username and user.validate_password(password):
        # 登录
        login_user(user)
        # 记录登录日志
        login_log(request, uid=user.id, is_access=True)
        # 授权路由存入session
        role = current_user.role
        user_power = []
        for i in role:
            if i.enable == 0:
                continue
            for p in i.power:
                if p.enable == 0:
                    continue
                user_power.append(p.code)
        session['permissions'] = user_power
        # # 角色存入session
        roles = []
        for role in current_user.role.all():
            roles.append(role.name)
        res = {
        'msg': '登录成功!',
        'code': 0,
        'user': {
            'username': user.username,
            'user_id': user.id,
            'role_name': roles[0] if bool(roles) else '普通用户'

        },
        'success': True
        }
        return jsonify(res)
    login_log(request, uid=user.id, is_access=False)
    return fail_api(msg="用户名或密码错误")


# 退出登录
@bp.post('/logout')
# @login_required => redirect to login page
def logout():
    logout_user()
    # session.pop('permissions') => error: KeyError: 'permissions'
    return success_api(msg="注销成功！")

@bp.post('/add')
def add():
    req_json = request.get_json(force=True)
    username = str_escape(req_json.get('username'))
    password = str_escape(req_json.get('password'))

    if not username or not password:
        return fail_api(msg="账号密码不得为空")

    if bool(User.query.filter_by(username=username).count()):
        return fail_api(msg="账号已经存在")
    user = User(username=username, enable=1)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return success_api(msg="增加成功")