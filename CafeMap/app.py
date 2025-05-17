from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import folium
import webbrowser
import os
from werkzeug.utils import secure_filename
from flask_wtf.file import FileAllowed

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/location.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Форма для добавления и редактирования локации
class LocationForm(FlaskForm):
    name = StringField('Название локации', validators=[DataRequired()])
    type = SelectField('Тип локации', choices=[
        ('Ресторан', 'Ресторан'),
        ('Кафе', 'Кафе'),
        ('Локация', 'Локация')
    ], validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    metro = StringField('Ближайшее метро', validators=[DataRequired()])
    coordinates = StringField('Координаты (широта, долгота)')
    map_link = StringField('Ссылка на Яндекс карты')
    photo = FileField('Фото локации', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    description = TextAreaField('Описание', validators=[DataRequired()])
    promo_code = StringField('Промокод')
    rating = StringField('Рейтинг (0-5)')
    submit = SubmitField('Сохранить')


# Добавление новой локации
@app.route('/add_location', methods=['GET', 'POST'])
@login_required
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        # Обработка загрузки фото
        photo_filename = None
        if form.photo.data:
            photo = form.photo.data
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_filename = f"img/{filename}"

        # Создание новой локации
        new_location = Location(
            name=form.name.data,
            type=form.type.data,
            address=form.address.data,
            metro=form.metro.data,
            coordinates=form.coordinates.data,
            map_link=form.map_link.data,
            photo=photo_filename if photo_filename else None,
            description=form.description.data,
            promo_code=form.promo_code.data,
            rating=float(form.rating.data) if form.rating.data else None
        )

        db.session.add(new_location)
        db.session.commit()
        flash('Локация успешно добавлена!', 'success')
        return redirect(url_for('show_locations'))

    return render_template('add_location.html', form=form)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def show_map_with_photos(self):
    """Создаёт карту с фотографиями и названиями всех локаций и открывает её в браузере"""
    # Центр карты
    map_center = [55.751244, 37.618423]
    moscow_map = folium.Map(location=map_center, zoom_start=12)

    """Получение данных из базы"""
    self.cursor.execute("SELECT name, description, coordinates, photo FROM locations")
    locations = self.cursor.fetchall()

    for location in locations:
        name, description, coordinates, photo_path = location

        try:
            coords = [float(coord) for coord in coordinates.split(",")]

            """ Преобразование пути к изображению в абсолютный"""
            photo_path = os.path.abspath(photo_path)

            """Проверка существования файла"""
            if not os.path.exists(photo_path):
                photo_path = ""  # Убираем фото, если файла нет

            # Создаём HTML-содержимое всплывающего окна
            popup_content = f"""
                <b>{name}</b><br>
                {description}<br>
                <img src="{photo_path}" alt="{name}" width="150">
                """
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=name
            ).add_to(moscow_map)
        except ValueError:
            print(f"Некорректные координаты для локации: {name}")

    # Сохраняем карту в HTML
    map_file = "locations_map_with_photos.html"
    moscow_map.save(map_file)

    # Открываем карту в браузере
    webbrowser.open(f"file://{os.path.abspath(map_file)}")


# Редактирование локации
@app.route('/edit_location/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_location(id):
    location = Location.query.get_or_404(id)
    form = LocationForm(obj=location)

    if form.validate_on_submit():
        # Обработка загрузки фото
        if form.photo.data:
            photo = form.photo.data
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                location.photo = f"img/{filename}"

        # Обновление данных локации
        location.name = form.name.data
        location.type = form.type.data
        location.address = form.address.data
        location.metro = form.metro.data
        location.coordinates = form.coordinates.data
        location.map_link = form.map_link.data
        location.description = form.description.data
        location.promo_code = form.promo_code.data
        location.rating = float(form.rating.data) if form.rating.data else None

        db.session.commit()
        flash('Локация успешно обновлена!', 'success')
        return redirect(url_for('show_locations'))

    return render_template('add_location.html', form=form, location=location)


# Удаление локации
@app.route('/delete_location/<int:id>', methods=['POST'])
@login_required
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash('Локация успешно удалена!', 'success')
    return redirect(url_for('show_locations'))


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


# Модель локации
class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Название локации
    type = db.Column(db.String(50), nullable=False)  # Тип локации
    address = db.Column(db.String(200), nullable=False)
    metro = db.Column(db.String(50), nullable=False)
    coordinates = db.Column(db.String(50))
    map_link = db.Column(db.String(500))  # Ссылка на Яндекс карты
    photo = db.Column(db.String(100))  # Путь к фото
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
    # Берем 6 локаций с самым высоким рейтингом
    top_locations = Location.query.order_by(Location.rating.desc()).limit(6).all()
    return render_template("index.html", top_locations=top_locations)


# Страница всех локаций
@app.route('/locations')
def show_locations():
    all_locations = Location.query.all()
    return render_template("locations.html", locations=all_locations)


# Страница о проекте
@app.route('/about')
def about():
    return render_template("about.html")


# Страница с локациями на карте
@app.route('/locations_map_with_photos')
def locations_map_with_photos():
    return render_template("locations_map_with_photos.html")


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
