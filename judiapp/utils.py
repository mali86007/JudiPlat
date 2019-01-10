from urllib.parse import urlparse, urljoin
from flask import current_app, request, redirect, url_for
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from .extensions import db
from .models import User
from .settings import Operations


def is_safe_url(target):
    """对URL进行安全验证"""
    ref_url = urlparse(request.host_url)        # 获取程序内的主机URL
    test_url = urlparse(urljoin(request.host_url, target))      # 拼接target完整的绝对路径
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc   # 网络协议正确并且两者网络位置一致则True


def redirect_back(default='main.index', **kwargs):
    """获取上个页面的URL"""
    for target in request.args.get('next'), request.referrer:   # 从request.referrer和查询参数next中查找上页面URL
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)     # 目标URL通过安全验证则重定向
    return redirect(url_for(default, **kwargs))     # 未找到或未通过安全验证，转默认URL


def generate_token(user, operation, expire_in=None, **kwargs):
    """生成令牌"""
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)     # expire_in过期时间，默认3600秒
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)                                           # 用参数更新字典
    return s.dumps(data)                                            # 返回写入数据的序列化对象


def validate_token(user, token, operation, new_password=None):
    """验证并解析令牌"""
    s = Serializer(current_app.config['SECRET_KEY'])                # 用相同密钥创建序列化对象
    try:
        data = s.loads(token)                                       # 接受令牌值，提取数据
    except (SignatureExpired, BadSignature):                        # 提取失败，抛出异常：签名过期、不匹配
        return False

    if operation != data.get('operation') or user.id != data.get('id'): # 验证用户id和操作类型是否有误
        return False

    if operation == Operations.CONFIRM:                             # 通过确认验证
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:                    # 通过重置密码验证
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:                      # 通过改变邮箱验证
        new_email = data.get('new_email')
        if new_email is None:               # 无原邮箱，返回False
            return False
        if User.query.filter_by(email=new_email).first() is not None:       # 邮箱重复，返回False
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True