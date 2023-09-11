from app import db, create_app
from app.models import User

app = create_app()
with app.app_context():
    login = input('Введите логин:')
    new_user = User.query.filter_by(login=login).update(
        {'show': 0})
    db.session.commit()
print(f'Пользователь {login} удален!')
