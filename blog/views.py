from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import Post, Purchase, User
from . import db
import markdown

main = Blueprint('main', __name__)

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', posts=posts)

@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.is_paid:
        if not current_user.is_authenticated:
            flash('请先登录后再查看付费文章', 'warning')
            return redirect(url_for('auth.login'))
        purchase = Purchase.query.filter_by(
            user_id=current_user.id,
            post_id=post_id,
            status='completed'
        ).first()
        if not purchase and current_user.id != post.author_id:
            return render_template('post_preview.html', post=post)
    
    # 将Markdown内容转换为HTML
    post.content = markdown.markdown(post.content, extensions=['fenced_code', 'tables'])
    return render_template('post.html', post=post)

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_paid = bool(request.form.get('is_paid'))
        price = float(request.form.get('price', 0)) if is_paid else 0
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return redirect(url_for('main.create_post'))
        
        if is_paid and price <= 0:
            flash('付费文章的价格必须大于0', 'error')
            return redirect(url_for('main.create_post'))
            
        try:
            post = Post(
                title=title,
                content=content,
                is_paid=is_paid,
                price=price,
                author_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            flash('文章发布成功！', 'success')
            return redirect(url_for('main.post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('发布失败，请稍后重试', 'error')
            return redirect(url_for('main.create_post'))
    
    return render_template('create_post.html')

@main.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('你没有权限编辑这篇文章', 'error')
        return redirect(url_for('main.post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_paid = bool(request.form.get('is_paid'))
        price = float(request.form.get('price', 0))
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return redirect(url_for('main.edit_post', post_id=post_id))
            
        try:
            post.title = title
            post.content = content
            post.is_paid = is_paid
            post.price = price
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('main.post', post_id=post_id))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请稍后重试', 'error')
            return redirect(url_for('main.edit_post', post_id=post_id))
    
    return render_template('edit_post.html', post=post)

@main.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('你没有权限删除这篇文章', 'error')
        return redirect(url_for('main.post', post_id=post_id))
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章已删除', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请稍后重试', 'error')
        return redirect(url_for('main.post', post_id=post_id))

@main.route('/create_purchase/<int:post_id>', methods=['POST'])
@login_required
def create_purchase(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.is_paid:
        flash('这不是付费文章', 'error')
        return redirect(url_for('main.post', post_id=post_id))
    
    if post.author_id == current_user.id:
        flash('这是你自己的文章', 'error')
        return redirect(url_for('main.post', post_id=post_id))
        
    existing_purchase = Purchase.query.filter_by(
        user_id=current_user.id,
        post_id=post_id,
        status='completed'
    ).first()
    
    if existing_purchase:
        flash('你已经购买过这篇文章了', 'info')
        return redirect(url_for('main.post', post_id=post_id))
    
    try:
        purchase = Purchase(
            user_id=current_user.id,
            post_id=post_id,
            amount=post.price,
            status='pending'
        )
        db.session.add(purchase)
        db.session.commit()
        # TODO: 接入支付系统
        return redirect(url_for('main.post', post_id=post_id))
    except Exception as e:
        db.session.rollback()
        flash('购买失败，请稍后重试', 'error')
        return redirect(url_for('main.post', post_id=post_id))
