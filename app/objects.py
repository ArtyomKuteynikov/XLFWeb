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

objects = Blueprint('objects', __name__)
