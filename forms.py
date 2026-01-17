from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    content = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('发表')

class CommentForm(FlaskForm):
    author = StringField('昵称', validators=[DataRequired()])
    content = TextAreaField('评论', validators=[DataRequired()])
    submit = SubmitField('提交评论')
