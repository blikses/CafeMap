from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Указываем путь к базе данных в папке instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/location.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/img'  # Папка для фотографий
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Модель локации (обновленная по вашей структуре)
class Location(db.Model):
    __tablename__ = 'locations'  # Явно указываем имя таблицы

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Название локации
    type = db.Column(db.String(50), nullable=False)  # Тип локации
    address = db.Column(db.String(200), nullable=False)
    metro = db.Column(db.String(50), nullable=False)
    coordinates = db.Column(db.String(50))
    map_link = db.Column(db.String(500))  # Ссылка на Яндекс карты
    photo = db.Column(db.String(100))  # Путь к фото (img/filename.jpg)
    description = db.Column(db.Text, nullable=False)
    promo_code = db.Column(db.String(50))  # Промокод
    rating = db.Column(db.Float)  # Рейтинг

    def __repr__(self):
        return f'<Location {self.name}>'


# Форма регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Email (необязательно)', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirm = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Зарегистрироваться')


# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Главная страница
@app.route('/')
@app.route('/home')
def index():
    top_locations = Location.query.order_by(Location.rating.desc()).limit(3).all()
    return render_template("index.html", locations=top_locations)


# Страница всех локаций
@app.route('/locations')
def show_locations():
    all_locations = Location.query.all()
    return render_template("locations.html", locations=all_locations)


# Страница о проекте
@app.route('/about')
def about():
    return render_template("about.html")


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует!', 'error')
            return redirect(url_for('register'))

        if form.email.data:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Этот email уже используется!', 'error')
                return redirect(url_for('register'))

        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
