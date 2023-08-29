from flask import redirect, Blueprint, url_for

index_bp = Blueprint('Index', __name__, url_prefix='/')


@index_bp.route('/')
def index():
    return redirect(url_for('passport.login'))
