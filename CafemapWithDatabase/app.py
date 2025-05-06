from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locations.db'
db = SQLAlchemy(app)


'''Создаем колонки в базе даных для добавления локаций'''


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)  # Название локации
    '''Не больше 300 символов и нельзя ввести пустое значение'''
    photo = db.Column(db.LargeBinary, nullable=False)
    '''Описание лоации'''
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    '''Когда будем выбирать какой-либо объект из этого класса, нам будет выдаваться объект и id'''
    def __repr__(self):
        return '<Article> %r' % self.id


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/locations')
def locations():
    return render_template("locations.html")

@app.route('/create-article')
def create_article():
    return render_template('create-article.html')

'''@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return 'User page: ' + name + " - " + str(id)'''


if __name__ == "__main__":
    app.run(debug=True)