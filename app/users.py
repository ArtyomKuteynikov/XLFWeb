# _XiuCNs7:@xu
import json
from datetime import datetime, timedelta
from os import getcwd
from flask import Blueprint, render_template, request, send_from_directory, make_response, session, redirect, url_for, \
    flash
from flask_login import login_required, current_user, logout_user
import os

from werkzeug.security import generate_password_hash

from . import db
from app.models import User, Payments, Shops

main = Blueprint('main', __name__)


@main.route('/', methods=['POST', 'GET'])
@main.route('/objects', methods=['POST', 'GET'])
@login_required
def objects():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    data = []
    if current_user.role == 1:
        objects = Shops.query.filter_by(user_id=current_user.id, show=1).all()
    else:
        objects = Shops.query.filter_by(show=1).all()
    for i in objects:
        client = User.query.filter_by(id=i.user_id).first()
        if client:
            data.append(
                {
                    'id': i.id,
                    'client': client.name,
                    'address': i.address,
                    'name': i.name,
                    'phone': i.phone,
                    'email': i.email,
                    'end': i.end.strftime("%d.%m.%Y") if i.end else '',
                    'ident': url_for('static', filename=f'ids/{i.ident}') if i.ident else ''
                }
            )
    users = User.query.filter_by(show=1, role=1).all()
    return render_template('stats.html', objects=data, users=users, page_title='Объекты',
                           enumerate=enumerate)


@main.route('/clients', methods=['POST', 'GET'])
@login_required
def clients():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    users_data = []
    if current_user.role == 2:
        users = User.query.filter_by(show=1, role=1).all()
        page_title = 'Клиенты'
    else:
        users = User.query.filter_by(show=1, role=2).all()
        page_title = 'Менеджеры'
    for i in users:
        users_data.append(
            {
                'id': i.id,
                'login': i.login,
                'name': i.name,
                'phone': i.phone,
                'email': i.email,
                'org_name': i.org_name,
                'status': 'Активен' if i.status == 'active' else 'Заблокирован'
            }
        )
    return render_template('users.html', users=users_data, page_title=page_title, enumerate=enumerate)


@main.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return {
            'id': user.id,
            'login': user.login,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'org_name': user.org_name
        }
    else:
        return {'message': 'User not found'}, 404


@main.route('/get_object/<int:object_id>', methods=['GET'])
def get_object(object_id):
    user = Shops.query.get(object_id)
    if user:
        return {
            'id': user.id,
            'address': user.address,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
        }
    else:
        return {'message': 'Оbject not found'}, 404


@main.route('/add_user', methods=['POST'])
def add_user():
    login = request.form.get('login')
    org_name = request.form.get('org_name')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    if User.query.filter_by(login=login.lower(), role=1 if current_user.role == 2 else 2).first():
        return {'message': 'Пользователь с таким логином уже зарегистрирован'}
    new_user = User(name=name, org_name=org_name, login=login, email=email, phone=phone,
                    password=generate_password_hash(password, method='sha256'), role=1 if current_user.role == 2 else 2,
                    show=1, status='active', registered=datetime.now())
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'Success'}


@main.route('/add_object', methods=['POST'])
def add_object():
    user = request.form.get('client')
    address = request.form.get('address')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    new_user = Shops(name=name, address=address, email=email, phone=phone, user_id=user, show=1,
                    registered=datetime.now())
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'Success'}


@main.route('/pay/<int:id>', methods=['POST'])
def pay(id):
    print(id)
    amount = request.form.get('amount')
    comment = request.form.get('comment')
    start = datetime.strptime(request.form.get('start'), '%Y-%m-%d')
    end = datetime.strptime(request.form.get('end'), '%Y-%m-%d')
    new_user = Payments(shop_id=id, amount=amount, comment=comment, start=start, end=end, show=1,
                    registered=datetime.now(), manager_id=current_user.id)
    db.session.add(new_user)
    db.session.commit()
    _ = Shops.query.filter_by(id=id).update({'end': end})
    db.session.commit()
    return {'message': 'Success'}


@main.route('/load_identification/<int:id>', methods=['POST'])
def load_identification(id):
    print(request.files)
    try:
        file = request.files['file']
        filename = 'IDFile' + str(id) + '.' + file.filename.split('.')[-1]
        file.save(r'/root/XLF/app/static/ids/' + filename)
        _ = Shops.query.filter_by(id=id).update({'ident': filename})
        db.session.commit()
        return {'message': 'Success'}
    except Exception as e:
        return {'message': str(e)+os.getcwd() + r'/app/static/ids/' + filename}


@main.route('/edit_user', methods=['POST'])
def edit_user():
    user_id = request.form.get('id')
    login = request.form.get('login')
    org_name = request.form.get('org_name')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    user = User.query.get(user_id)
    if user:
        user.login = login.lower()
        user.org_name = org_name
        user.name = name
        user.email = email
        user.phone = phone
        db.session.commit()
        return {'message': 'Success'}
    else:
        return {'message': 'User not found'}, 404


@main.route('/edit_object', methods=['POST'])
def edit_object():
    object_id = request.form.get('id')
    address = request.form.get('address')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    object = Shops.query.get(object_id)
    if object:
        object.address = address
        object.name = name
        object.email = email
        object.phone = phone
        db.session.commit()
        return {'message': 'Success'}
    else:
        return {'message': 'User not found'}, 404


@main.route('/password_user/<id>', methods=['POST'])
def password_user(id):
    password = request.form.get('password')
    user = User.query.get(id)
    if user:
        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()
        return {'message': 'Success'}
    else:
        return {'message': 'Вы не выбрали пользователя'}


@main.route('/block_users', methods=['POST'])
def block_users():
    user_ids = request.form.get('user_ids')
    if not user_ids:
        return {"message": "No users selected"}, 400
    for user_id in user_ids.split('#')[:-1]:
        user = User.query.get(int(user_id))
        if user:
            user.status = 'blocked'
            db.session.commit()
    return {"message": "Success"}


@main.route('/unblock_users', methods=['POST'])
def unblock_users():
    user_ids = request.form.get('user_ids')
    if not user_ids:
        return {"message": "No users selected"}, 400
    for user_id in user_ids.split('#')[:-1]:
        user = User.query.get(int(user_id))
        if user:
            user.status = 'active'
            db.session.commit()
    return {"message": "Success"}


@main.route('/delete_users', methods=['POST'])
def delete_users():
    user_ids = request.form.get('user_ids')
    if not user_ids:
        return {"message": "No users selected"}, 400
    for user_id in user_ids.split('#')[:-1]:
        user = User.query.get(int(user_id))
        if user:
            user.show = 0
            db.session.commit()
    return {"message": "Success"}


@main.route('/delete_objects', methods=['POST'])
def delete_objects():
    object_ids = request.form.get('object_ids')
    if not object_ids:
        return {"message": "No users selected"}, 400
    for object_id in object_ids.split('#')[:-1]:
        object = Shops.query.get(int(object_id))
        if object:
            object.show = 0
            db.session.commit()
    return {"message": "Success"}


@main.route('/sales', methods=['POST', 'GET'])
@login_required
def sales():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    result = []
    data = []
    filtered = False
    object_search = ''
    client_search = ''
    manager_search = ''
    comment_search = ''
    amount_search = ''
    start_raw = (datetime.now() - timedelta(days=91)).strftime('%Y-%m-%d')
    finish_raw = (datetime.now()).strftime('%Y-%m-%d')
    date = ''
    if current_user.role == 1:
        for i in Shops.query.filter_by(user_id=current_user.id).all():
            if amount_search:
                data += Payments.query.filter_by(shop_id=i.id, show=1, amount=amount_search).all()
            else:
                data += Payments.query.filter_by(shop_id=i.id, show=1).all()
    else:
        if amount_search:
            data += Payments.query.filter_by(show=1, amount=amount_search).all()
        else:
            data += Payments.query.filter_by(show=1).all()
    print(data, bool(amount_search), amount_search)
    start = datetime.strptime(start_raw, '%Y-%m-%d')
    finish = datetime.strptime(finish_raw, '%Y-%m-%d')
    for i in data:
        if Shops.query.filter_by(id=i.shop_id).first():
            object = Shops.query.filter_by(id=i.shop_id).first().address
            manager = User.query.filter_by(id=i.manager_id).first().name
            client = User.query.filter_by(id=Shops.query.filter_by(id=i.shop_id).first().user_id).first().org_name
            if True:
                result.append(
                    {
                        'object': object,
                        'client': client,
                        'manager': manager,
                        'id': i.id,
                        'registered': i.registered.strftime("%d.%m.%Y"),
                        'amount': i.amount,
                        'start': i.start.strftime("%d.%m.%Y"),
                        'end': i.end.strftime("%d.%m.%Y"),
                        'comment': i.comment
                    }
                )
    start_raw = (datetime.now() - timedelta(days=91)).strftime('%Y-%m-%d')
    finish_raw = (datetime.now() + timedelta(days=91)).strftime('%Y-%m-%d')
    today_raw = datetime.now().strftime('%Y-%m-%d')
    return render_template('sales.html', start=start_raw, finish=finish_raw, today=today_raw,
                           data=result, object=object_search, filtered=filtered, client=client_search,
                           manager=manager_search, comment=comment_search, page_title='История',
                           date=date.strftime('%Y-%m-%d') if date else '', amount=amount_search if amount_search else '', enumerate=enumerate)


@main.route('/org/<id>', methods=['GET'])
@main.route('/user/<id>', methods=['GET'])
@login_required
def user(id):
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(id=id).first()
    return render_template('people/user.html', user=user, enumerate=enumerate)


@main.route('/block/<id>', methods=['GET'])
@login_required
def block(id):
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    _ = User.query.filter_by(id=id).update({'status': 'blocked'})
    db.session.commit()
    user = User.query.filter_by(id=id).first()
    if user.is_uk:
        return redirect(url_for('main.uk', id=id))
    return redirect(url_for('main.user', id=id))


@main.route('/profile')
@login_required
def profile():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('profile.html', page_title="Профиль")


@main.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    org_name = request.form.get('org')
    phone = request.form.get('phone').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                                  '')
    name = request.form.get('name')
    email = request.form.get('email')
    _ = User.query.filter_by(id=current_user.id).update(
        {'name': name, 'org_name': org_name, 'email': email, 'phone': phone})
    db.session.commit()
    return redirect(url_for('main.profile'))


@main.route('/update-password', methods=['GET'])
@login_required
def update_password():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('update-password.html', page_title="Смена пароля")


@main.route('/update-password', methods=['POST'])
@login_required
def update_password_post():
    if current_user.show == 0:
        logout_user()
        return redirect(url_for('auth.login'))
    password = request.form.get('password')
    password_conf = request.form.get('password-conf')
    if password != password_conf:
        flash('Пароли не совпадают')
        return redirect(url_for('main.update_password'))
    _ = User.query.filter_by(id=current_user.id).update({'password': generate_password_hash(password, method='sha256')})
    db.session.commit()
    return redirect(url_for('main.update_password'))
