from flask import Blueprint, url_for, render_template, redirect, request
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import sqlalchemy
import re
from models import db, Users

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

register = Blueprint('register', __name__, template_folder='../frontend')
login_manager = LoginManager()
login_manager.init_app(register)

@register.route('/register', methods=['GET', 'POST'])
def show():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if username and email and password and confirm_password:
            # Check if email format is valid
            if not is_valid_email(email):
                return redirect(url_for('register.show') + '?error=invalid-email')

            # Check if passwords match
            if password == confirm_password:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                try:
                    new_user = Users(
                        username=username,
                        email=email,
                        password=hashed_password,
                    )

                    db.session.add(new_user)
                    db.session.commit()
                except sqlalchemy.exc.IntegrityError:
                    return redirect(url_for('register.show') + '?error=user-or-email-exists')

                return redirect(url_for('login.show') + '?success=account-created')
            else:
                return redirect(url_for('register.show') + '?error=passwords-do-not-match')
        else:
            return redirect(url_for('register.show') + '?error=missing-fields')
    else:
        return render_template('register.html')
