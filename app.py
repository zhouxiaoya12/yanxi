from flask import (
    Flask, render_template, redirect,
    url_for, request, session, send_from_directory
)
from models import db, Post, Comment
from forms import PostForm, CommentForm
from werkzeug.utils import secure_filename
import os

# ======================
# Flask 基础配置（原有）
# ======================

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'video-blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 初始化数据库
with app.app_context():
    db.create_all()

# ======================
# 新增：视频文件夹配置
# ======================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, 'uploads', 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)

VIDEO_PASSWORD = "123456"   # 私密文件夹访问密码

# ======================
# 原有博客功能
# ======================

# 首页：显示所有文章
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# 查看单篇文章 + 评论
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            author=form.author.data,
            content=form.content.data,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('post.html', post=post, form=form)

# 新建文章
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    # ⚠️ 你原来这里 render 了 base.html
    # 如果你有单独的新建页面模板，后续可以换
    return render_template('new_post.html', form=form)

# ======================
# 新增：私密视频功能
# ======================

# 视频密码验证页
@app.route('/videos/login', methods=['GET', 'POST'])
def video_login():
    print("method:", request.method)
    print("password:", request.form.get("password"))
    
    if request.method == 'POST':
        if request.form.get('password') == VIDEO_PASSWORD:
            session['video_auth'] = True
            return redirect(url_for('video_folder'))
    return render_template('video_login.html')

# 视频文件夹（受保护）
@app.route('/videos')
def video_folder():
    if not session.get('video_auth'):
        return redirect(url_for('video_login'))

    videos = [
        f for f in os.listdir(VIDEO_DIR)
        if f.lower().endswith('.mp4')
    ]

    return render_template('video_folder.html', videos=videos)

# 上传视频
@app.route('/videos/upload', methods=['POST'])
def upload_video():
    if not session.get('video_auth'):
        return redirect(url_for('video_login'))

    file = request.files.get('video')
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(VIDEO_DIR, filename))

    return redirect(url_for('video_folder'))

# 受保护的视频访问（防直链）
@app.route('/uploads/videos/<filename>')
def serve_video(filename):
    if not session.get('video_auth'):
        return redirect(url_for('video_login'))

    return send_from_directory(VIDEO_DIR, filename)

##删除文章butten

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 如果你模型里没设置级联删除，这里手动删评论
    for comment in post.comments:
        db.session.delete(comment)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('index'))


# ======================
# 启动
# ======================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
