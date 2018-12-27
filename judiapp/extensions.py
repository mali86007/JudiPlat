from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
# from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate

bootstrap = Bootstrap()             # bootstrap实例
db = SQLAlchemy()                   # 数据模型实例
login_manager = LoginManager()      # 用户管理实例
csrf = CSRFProtect()                # CSRF令牌实例
ckeditor = CKEditor()               # 富文本编辑器实例
mail = Mail()                       # 电子邮箱实例
moment = Moment()                   # 本地化实例
# toolbar = DebugToolbarExtension()
migrate = Migrate()                 # 数据库迁移实例

@login_manager.user_loader
def load_user(user_id):
    from judiapp.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'user.login'     # 定义登录视图的名称，可用于用户未授权操作的跳转
login_manager.login_message_category = 'warning'    # 定义提醒消息分类


class Guest(AnonymousUserMixin):

    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = Guest