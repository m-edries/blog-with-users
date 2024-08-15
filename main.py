from flask import Flask, render_template, redirect, url_for, flash, session, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
# from flask_gravatar import Gravatar
from db_tables import Blogs, Users, Comments
from datetime import date
from functools import wraps
import hashlib
# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv

app = Flask(__name__)
# loading variables from .env file
load_dotenv()
# accessing a value
app.config['SECRET_KEY'] = os.getenv("my_secret_key")
ckeditor = CKEditor(app)
Bootstrap(app)

# Gravatar
# gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False,
#                     force_lower=False, use_ssl=False, base_url=None)


# Add Context Processor: If you want to make the get_gravatar_url function available in all templates,
# add it as a context processor in your Flask app.
@app.context_processor
def inject_gravatar_url():
    return dict(get_gravatar_url=get_gravatar_url)


def get_gravatar_url(email, size=200, default='mp'):
    base_url = 'https://www.gravatar.com/avatar/'
    hash_email = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"{base_url}{hash_email}?s={size}&d={default}"


# CONNECT TO DB
user = Users()
blog = Blogs()
comment = Comments()

# Authentication.
login_manager = LoginManager()
login_manager.init_app(app)


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return user.get_user_by_id(user_id)


@app.route('/')
def get_all_posts():
    posts = blog.get_all_posts()
    return render_template("index.html", all_posts=posts)


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name_ = form.name.data
        email_ = form.email.data
        password_ = form.password.data
        if user.get_user_by_email(email_):
            flash('You have already signed up with that email, log in instead!')
            return redirect(url_for("login"))
        else:
            hash_and_salted_password = generate_password_hash(password=password_, method="pbkdf2:sha256", salt_length=8)
            new_user = user.insert_user(email_, hash_and_salted_password, name_)
            # Log in and authenticate user after adding details to database.
            login_user(new_user)
            flash('You were successfully logged in')
            return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        new_user = user.get_user_by_email(email)
        if new_user:
            # Check stored password hash against entered password hashed.
            if check_password_hash(new_user.password, password):
                login_user(new_user)
                flash('You were successfully logged in')
                return redirect(url_for("get_all_posts"))
            else:
                error = "Invalid credentials: maybe you entered an incorrect password."
        else:
            error = "Invalid credentials: maybe you entered an incorrect email."
    return render_template("login.html", form=form, error=error)


@app.route('/logout')
def logout():
    session['_flashes'].clear()
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = blog.get_post_by_id(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment_text = form.comment.data
            comment.insert_comment(comment_text, current_user.id, post_id)
            return redirect(url_for('show_post', post_id=post_id))
        else:
            flash("You need to login or register to comment")
            return redirect(url_for("login"))
    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        title_ = form.title.data
        subtitle_ = form.subtitle.data
        body_ = form.body.data
        img_url_ = form.img_url.data
        author_id = current_user.id
        date_ = date.today().strftime("%B %d, %Y")
        blog.add_new_post(title_, subtitle_, body_, img_url_, author_id, date_)
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(post_id):
    post = blog.get_post_by_id(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        title_ = edit_form.title.data
        subtitle_ = edit_form.subtitle.data
        img_url_ = edit_form.img_url.data
        body_ = edit_form.body.data
        blog.update_post(post_id, title_, subtitle_, img_url_, body_)
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@login_required
@admin_only
def delete_post(post_id):
    blog.delete_post(post_id)
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=False, host='0.0.0.0', port=5000)
