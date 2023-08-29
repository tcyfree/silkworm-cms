from flask import Blueprint, session, redirect, url_for, render_template, request
from flask_login import current_user, login_user, login_required, logout_user

from applications.common import admin as index_curd
from applications.common.admin_log import login_log
from applications.common.utils.http import fail_api, success_api
from applications.models import User, Role
from applications.extensions import db
from applications.common.utils.validate import str_escape

passport_bp = Blueprint('passport', __name__, url_prefix='/passport')


def register_passport_views(app):
    app.register_blueprint(passport_bp)


# 获取验证码
@passport_bp.get('/getCaptcha')
def get_captcha():
    resp, code = index_curd.get_captcha()
    session["code"] = code
    return resp


# 登录
@passport_bp.get('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html')


# 登录
@passport_bp.post('/login')
def login_post():
    req = request.form
    username = req.get('username')
    password = req.get('password')
    code = req.get('captcha').__str__().lower()

    if not username or not password or not code:
        return fail_api(msg="用户名或密码没有输入")
    s_code = session.get("code", None)
    session["code"] = None

    if not all([code, s_code]):
        return fail_api(msg="参数错误")

    if code != s_code:
        return fail_api(msg="验证码错误")
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
        # roles = []
        # for role in current_user.role.all():
        #     roles.append(role.id)
        # session['role'] = [roles]

        return success_api(msg="登录成功")
    login_log(request, uid=user.id, is_access=False)
    return fail_api(msg="用户名或密码错误")


# 退出登录
@passport_bp.post('/logout')
@login_required
def logout():
    logout_user()
    session.pop('permissions')
    return success_api(msg="注销成功")


# 注册
@passport_bp.post('/register')
def register():
    req_json = request.get_json(force=True)
    # a = req_json.get("roleIds", default=2)
    username = str_escape(req_json.get('username'))
    real_name = str_escape(req_json.get('realname'))
    password = str_escape(req_json.get('password'))
    # role_ids = a.split(',')

    if not username or not real_name or not password:
        return fail_api(msg="账号姓名密码不得为空")

    if bool(User.query.filter_by(username=username).count()):
        return fail_api(msg="用户已经存在")

    user = User(username=username, realname=real_name)
    user.set_password(password)
    db.session.add(user)
    # roles = Role.query.filter(Role.id.in_(role_ids)).all()
    # for r in roles:
    #     user.role.append(r)
    db.session.commit()
    return redirect(url_for("passport.login"))

