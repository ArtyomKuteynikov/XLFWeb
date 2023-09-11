from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    login = input('Введите логин:')
    if User.query.filter_by(login=login).first():
        print('Если данные обновлять не требуется - оставьте поле пустым')
        password = input('Введите новый пароль:')
        if password:
            _ = User.query.filter_by(login=login).update(
                {'password': generate_password_hash(password, method='sha256')})
            db.session.commit()
        name = input('Введите новый ФИО:')
        if name:
            _ = User.query.filter_by(login=login).update(
                {'name': name})
            db.session.commit()
        phone = input('Введите новый номер телефона:')
        if phone:
            _ = User.query.filter_by(login=login).update(
                {'phone': phone})
            db.session.commit()
        email = input('Введите новый e-mail:')
        if email:
            _ = User.query.filter_by(login=login).update(
                {'email': email})
            db.session.commit()
        print(f'Данные пользователя {login} обновлены!')
    else:
        print(f'Ошибка! Пользователь с логином {login} не существует!')
