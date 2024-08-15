from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, URL, Email
# from flask_ckeditor import CKEditorField


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[InputRequired()])
    subtitle = StringField("Subtitle", validators=[InputRequired()])
    img_url = StringField("Blog Image URL", validators=[InputRequired(), URL()])
    # body = CKEditorField("Blog Content", validators=[InputRequired()])
    body = TextAreaField("Blog Content", validators=[InputRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    name = StringField("Name", validators=[InputRequired()])
    submit = SubmitField("SIGN ME UP!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = StringField("Password", validators=[InputRequired()])
    submit = SubmitField("LET ME IN!")


class CommentForm(FlaskForm):
    # comment = CKEditorField("Comment", validators=[InputRequired()])
    comment = TextAreaField("Comment", validators=[InputRequired()])
    submit = SubmitField("SUBMIT COMMENT")
