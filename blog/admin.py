from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Post, User, Purchase
from . import db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('需要管理员权限', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def admin_panel():
    users = User.query.all()
    posts = Post.query.all()
    purchases = Purchase.query.all()
    return render_template('admin/panel.html', users=users, posts=posts, purchases=purchases)

@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/posts')
@admin_required
def manage_posts():
    posts = Post.query.all()
    return render_template('admin/posts.html', posts=posts)

@admin_bp.route('/purchases')
@admin_required
def manage_purchases():
    purchases = Purchase.query.all()
    return render_template('admin/purchases.html', purchases=purchases)
