# _XiuCNs7:@xu
import json
from datetime import datetime, timedelta
from os import getcwd
from flask import Blueprint, render_template, request, send_from_directory, make_response, session, redirect, url_for, \
    flash
from flask_login import login_required, current_user
import os
from . import db
from app.models import User, Payments, Shops

main = Blueprint('main', __name__)


@main.route('/', methods=['POST', 'GET'])
@main.route('/objects', methods=['POST', 'GET'])
@login_required
def objects():
    data = []
    objects = Shops.query.filter_by(user_id=current_user.id, show=1).all()
    for i in objects:
        data.append(
            {
                'id': i.id,
                'address': i.address,
                'name': i.name,
                'phone': i.phone,
                'email': i.email,
                'end': i.end.strftime("%m/%d/%Y")
            }
        )
    return render_template('stats.html', objects=data)


@main.route('/sales', methods=['POST', 'GET'])
def sales():
    result = []
    data = []
    print(current_user.role)
    if current_user.role == 1:
        for i in Shops.query.filter_by(user_id=current_user.id).all():
            data += Payments.query.filter_by(shop_id=i.id, show=1).all()
    else:
        data = Payments.query.filter_by(show=1).all()
    print(data)
    if request.method == 'POST':
        filtered = True
        object_search = request.form.get('object') if request.form.get('object') else ''
        client_search = request.form.get('client') if request.form.get('client') else ''
        manager_search = request.form.get('manager') if request.form.get('manager') else ''
        comment_search = request.form.get('comment') if request.form.get('comment') else ''
        start_raw = request.form.get('start') if request.form.get('start') else (
                    datetime.now() - timedelta(days=91)).strftime('%Y-%m-%d')
        finish_raw = request.form.get('finish') if request.form.get('finish') else (
                    datetime.now() + timedelta(days=91)).strftime('%Y-%m-%d')
    else:
        filtered = False
        object_search = ''
        client_search = ''
        manager_search = ''
        comment_search = ''
        start_raw = (datetime.now() - timedelta(days=91)).strftime('%Y-%m-%d')
        finish_raw = (datetime.now() + timedelta(days=91)).strftime('%Y-%m-%d')
    start = datetime.strptime(start_raw, '%Y-%m-%d')
    finish = datetime.strptime(finish_raw, '%Y-%m-%d')
    for i in data:
        object = Shops.query.filter_by(id=i.shop_id).first().address
        manager = User.query.filter_by(id=i.manager_id).first().name
        client = User.query.filter_by(id=Shops.query.filter_by(id=i.shop_id).first().user_id).first().org_name
        if object_search.lower() in str(
                object).lower() and start < i.start and finish > i.end and comment_search.lower() in str(
                i.comment).lower() and client_search.lower() in str(client).lower() and manager_search.lower() in str(
                manager).lower():
            result.append(
                {
                    'object': object,
                    'client': client,
                    'manager': manager,
                    'id': i.id,
                    'registered': i.registered.strftime("%m/%d/%Y"),
                    'amount': i.amount,
                    'start': i.start.strftime("%m/%d/%Y"),
                    'end': i.end.strftime("%m/%d/%Y"),
                    'comment': i.comment
                }
            )
    return render_template('sales.html', start=start.strftime('%Y-%m-%d'), finish=finish.strftime('%Y-%m-%d'),
                           data=result, object=object_search, filtered=filtered, client=client_search,
                           manager=manager_search, comment=comment_search)


@main.route('/org/<id>', methods=['GET'])
@main.route('/user/<id>', methods=['GET'])
@login_required
def user(id):
    user = User.query.filter_by(id=id).first()
    return render_template('people/user.html', user=user)


@main.route('/block/<id>', methods=['GET'])
@login_required
def block(id):
    _ = User.query.filter_by(id=id).update({'status': 'blocked'})
    db.session.commit()
    user = User.query.filter_by(id=id).first()
    if user.is_uk:
        return redirect(url_for('main.uk', id=id))
    return redirect(url_for('main.user', id=id))


@main.route('/unblock/<id>', methods=['GET'])
@login_required
def unblock(id):
    _ = User.query.filter_by(id=id).update({'status': 'inactive'})
    db.session.commit()
    user = User.query.filter_by(id=id).first()
    if user.is_uk:
        return redirect(url_for('main.uk', id=id))
    return redirect(url_for('main.user', id=id))


@main.route('/org/<id>', methods=['POST'])
@main.route('/user/<id>', methods=['POST'])
@login_required
def user_post(id):
    org_name = request.form.get('org_name')
    inn = request.form.get('inn')
    phone = request.form.get('phone').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                                  '')
    name = request.form.get('name')
    surname = request.form.get('surname')
    second_name = request.form.get('second_name')
    jk = request.form.get('jk')
    address = request.form.get('address')
    user = User.query.filter_by(id=id).first()
    if user.org:
        _ = User.query.filter_by(id=user.id).update({'name': name, 'surname': surname, 'second_name': second_name,
                                                     'address': address, 'inn': inn, 'org_name': org_name,
                                                     'jk': jk, 'phone': phone})
    else:
        _ = User.query.filter_by(id=user.id).update(
            {'name': name, 'surname': surname, 'address': address, 'jk': jk, 'phone': phone})
    db.session.commit()
    if user.is_uk:
        return redirect(url_for('main.uk', id=id))
    return redirect(url_for('main.user', id=id))


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@main.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    org_name = request.form.get('org')
    phone = request.form.get('phone').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                                  '')
    name = request.form.get('name')
    email = request.form.get('email')
    login = request.form.get('login')
    if current_user.login != login and User.query.filter_by(login=login, role=current_user.role):
        flash('Пользователь с таким логином уже существует в вашей группе')
        return redirect(url_for('main.profile'))
    _ = User.query.filter_by(id=current_user.id).update(
        {'name': name, 'org_name': org_name, 'email': email, 'login': login, 'phone': phone})
    db.session.commit()
    return redirect(url_for('main.profile'))
