import os
import datetime as dt

from flask import Flask, flash, redirect, request, url_for, send_from_directory, render_template
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)) + r'\uploads')
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'xlsx', 'png', 'jpg', 'avi', 'mp4', 'mp3', 'wav'}

app = Flask(__name__)
app.secret_key = '123456789'
api = Api(app)
app.config['MAX_CONTENT_LENGHT'] = 8 * 1000 * 1000
with app.app_context():
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datebase.db'
    db = SQLAlchemy(app)

    class FileModel(db.Model):
        __tablename__ = 'files'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False, unique=True)
        size = db.Column(db.Integer, nullable=False)
        file_ext = db.Column(db.String(10), nullable=False)
        created = db.Column(db.DateTime(), default=dt.datetime.now)
    db.create_all()


def allowed_file(filename):
    fix_filename = filename.replace(' ' or '-', '_')
    return '.' in fix_filename and fix_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_ext_file(filename):
    return filename.rsplit('.', 1)[1].lower()


@app.route('/')
def index():
    timer = dt.datetime.now()
    return render_template('index.html', context=timer)


@app.route('/files/create/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Не возможно прочитать файл')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Файл для загрузки не выбран')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file_size = 0
            file_ext = get_ext_file(filename)
            new_file = FileModel(name=filename, size=file_size, file_ext=file_ext)
            db.session.add(new_file)
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')


@app.route('/uploads/<name>', methods=['GET', 'POST'])
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)


@app.route('/files/get/<f_id>')
def get_id(f_id):
    file_id = FileModel.query.filter(FileModel.id == f_id)
    return render_template('get.html', list=file_id)


@app.route('/files/get/list', methods=['GET'])
def get_list():
    file_list = FileModel.query.order_by(FileModel.name).all()
    return render_template('get.html', list=file_list)


@app.route('/files/delete/<filename>', methods=['POST'])
def delete_file(filename):
    FileModel.query.filter(FileModel.name == filename).delete()
    db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('get.html')


if __name__ == '__main__':
    app.run(debug=True)
