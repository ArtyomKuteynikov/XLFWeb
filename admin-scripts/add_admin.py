from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash
import datetime

app = create_app()
with app.app_context():
    login = input('Введите логин:')
    password = input('Введите пароль:')
    name = input('Введите ФИО:')
    phone = input('Введите номер телефона:')
    email = input('Введите e-mail:')
    if User.query.filter_by(login=login).first():
        print(f'Ошибка! Пользователь с логином {login} уже существует!')
    else:
        new_user = User(login=login, password=generate_password_hash(password, method='sha256'), name=name, phone=phone, email=email,
                        registered=datetime.datetime.now(), role=3)

        db.session.add(new_user)
        db.session.commit()
        print(f'Пользователь {login} создан!')
