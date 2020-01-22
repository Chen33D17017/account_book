import os
import secrets
from PIL import Image
from account_book import db
from flask import current_app

def absolute_path(path):
    return os.path.join(current_app.root_path, 'static/profile_pics', path)


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    create_dir(os.path.join(current_app.root_path, 'static/profile_pics'))
    picture_path = absolute_path(picture_fn)
    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def delete_old_pic(old_pic):
    if old_pic != 'default.jpg':
        os.remove(absolute_path(old_pic))


