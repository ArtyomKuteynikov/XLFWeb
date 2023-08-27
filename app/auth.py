# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.models import User, Codes

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    login = request.form.get('login')
    password = request.form.get('password')
    type_ = request.form.get('type')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(login=login, role=type_, show=1).first()
    if not user:
        flash(f'Такого {"Пользователя" if int(type_) == 1 else "Менеджера" if int(type_) == 2 else "Администратора"} не существует')
        return redirect(url_for('auth.login'))
    if user.status == 'blocked':
        flash('Аккаунт заблокирован')
        return redirect(url_for('auth.login'))
    if not check_password_hash(user.password, password):
        flash('Неверный пароль')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    return redirect(url_for('main.objects'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
