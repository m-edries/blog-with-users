# Create a New Database.
from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB = "sqlite:///blog.db"
Base = declarative_base()


class Blogs(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    subtitle = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    img_url = Column(String(250), nullable=False)
    # Create Foreign Key, "user.id" the user refers to the tablename of User.
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    # The author property of Blogs is now a User object.
    post_author = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="blog_post")

    def add_new_post(self, title_, subtitle_, body_, img_url_, author_id, date_):
        new_post = Blogs(title=title_, subtitle=subtitle_, body=body_, img_url=img_url_, author_id=author_id, date=date_)
        session.add(new_post)
        session.commit()
        return new_post

    def get_all_posts(self):
        posts = session.query(Blogs).all()
        return posts

    def get_post_by_id(self, index):
        post = session.query(Blogs).filter_by(id=index).first()
        return post

    def update_post(self, id_, title_, subtitle_, img_url_, body_):
        session.query(Blogs).filter_by(id=id_).update({
            'title': title_,
            'subtitle': subtitle_,
            'body': body_,
            'img_url': img_url_,
        })
        session.commit()

    def delete_post(self, id_):
        session.query(Blogs).filter_by(id=id_).delete()
        session.commit()


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(Text, nullable=False)

    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    comment_author = relationship("Users", back_populates="comments")

    post_id = Column(Integer, ForeignKey("blog_posts.id"), nullable=False)
    blog_post = relationship("Blogs", back_populates="comments")

    def insert_comment(self, comment_text, author_id, post_id):
        new_comment = Comments(text=comment_text, author_id=author_id, post_id=post_id)
        session.add(new_comment)
        session.commit()
        return new_comment


class Users(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    name = Column(String(1000), nullable=False)
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("Blogs", back_populates="post_author")
    comments = relationship("Comments", back_populates="comment_author")

    # Insert a new user
    def insert_user(self, email, password, name):
        new_user = Users(email=email, password=password, name=name)
        session.add(new_user)
        session.commit()
        return new_user

    # Query the user
    def get_user_by_id(self, index):
        user = session.query(Users).filter_by(id=index).first()
        return user

    def get_user_by_email(self, email):
        user = session.query(Users).filter_by(email=email).first()
        return user

    # Query the data
    def get_all_users(self):
        results = session.query(Users).all()
        return results


# Create an engine and session
engine = create_engine(DB)
Session = sessionmaker(bind=engine)
session = Session()

# Create the table in the database
Base.metadata.create_all(engine)
