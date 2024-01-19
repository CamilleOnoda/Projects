from flask import Flask, redirect, render_template, url_for, request, flash, session, abort
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, SelectMultipleField, SubmitField, widgets
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
Bootstrap5(app)
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['SECRET_KEY'] = SECRET_KEY


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///coffee-wifi.db")
db = SQLAlchemy()
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Let me in!", validators=[DataRequired()])


class Cafeform(FlaskForm):
    cafe = StringField('Cafe', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    open_hours = StringField('Opening hours (e.g. 8am - 5pm)', validators=[DataRequired()])
    closed_choices = [
        ('Always open', 'Always open'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    closed = SelectMultipleField('Closed', choices=closed_choices, 
                                 validators=[DataRequired()], 
                                 widget=widgets.ListWidget(prefix_label=False), 
                                 option_widget=widgets.CheckboxInput())
    sweets = SelectField('Sweets', choices=[('🍰', '🍰'),
                                            ('🍰🍰', '🍰🍰'),
                                            ('🍰🍰🍰', '🍰🍰🍰'),
                                            ('🍰🍰🍰🍰', '🍰🍰🍰🍰'),
                                            ('🍰🍰🍰🍰🍰', '🍰🍰🍰🍰🍰')],
                                            validators=[DataRequired()])
    coffee = SelectField('Coffee', choices=[('☕', '☕'), ('☕☕', '☕☕'),
                                            ('☕☕☕', '☕☕☕'),
                                            ('☕☕☕☕', '☕☕☕☕'),
                                            ('☕☕☕☕☕', '☕☕☕☕☕')],
                                            validators=[DataRequired()])
    wifi = SelectField('Wifi', choices=[('✘', '✘'), ('💪', '💪'),
                                        ('💪💪', '💪💪'),
                                        ('💪💪💪', '💪💪💪'),
                                        ('💪💪💪💪', '💪💪💪💪'),
                                        ('💪💪💪💪💪', '💪💪💪💪💪')],
                                        validators=[DataRequired()])
    power = SelectField('Power', choices=[('✘', '✘'), ('⚡', '⚡'),
                                          ('⚡⚡', '⚡⚡'),
                                          ('⚡⚡⚡', '⚡⚡⚡'),
                                          ('⚡⚡⚡⚡', '⚡⚡⚡⚡'),
                                          ('⚡⚡⚡⚡⚡', '⚡⚡⚡⚡⚡')],
                                          validators=[DataRequired()])
    submit = SubmitField("✅ Confirm", validators=[DataRequired()])

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }


class Cafe(BaseModel, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cafe = db.Column(db.String(250), unique=True, nullable=False)
    city = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), unique=True, nullable=False)
    open_hours = db.Column(db.String(250), nullable=False )
    closed = db.Column(db.String(250), nullable=False)
    sweets = db.Column(db.String(250), nullable=False)
    coffee = db.Column(db.String(250), nullable=False)
    wifi = db.Column(db.String(250), nullable=False)
    power = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        is_admin = (username == 'admin')

        result = db.session.execute(db.select(User).where(User.username == username))
        user = result.scalar()
        if user:
            flash("This username already exist. Choose another one or log in instead.")
            return redirect(url_for('register'))
        
        hashed_salted_password = generate_password_hash(form.password.data,
                                                        method='pbkdf2:sha256',
                                                        salt_length=8)
        new_user = User(password = hashed_salted_password,
                        username = form.username.data,
                        is_admin = is_admin)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session['name'] = new_user.username
        return redirect(url_for('cafes'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.username == username))
        user = result.scalar()
        if not user:
            flash("This username does not exist. Register instead.")
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.")
        else:
            login_user(user)
            session['name'] = user.username
            return redirect(url_for('cafes'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/cafes')
@login_required
def cafes():
    name = current_user.username if current_user.is_authenticated else ''
    cafes_list = list(db.session.execute(db.select(Cafe).order_by(Cafe.city)).scalars())
    return render_template('cafes.html', cafes_list=cafes_list, name=name, logged_in=True)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = Cafeform()
    if form.validate_on_submit():
        closed_days = ' '.join(form.closed.data)
        new_cafe= Cafe(
            cafe=form.cafe.data,
            city=form.city.data,
            location=form.location.data,
            open_hours=form.open_hours.data,
            closed=closed_days,
            sweets=form.sweets.data,
            coffee=form.coffee.data,
            wifi=form.wifi.data,
            power=form.power.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    cafe_to_edit_id = request.args.get('id')
    cafe = db.get_or_404(Cafe, cafe_to_edit_id)
    if cafe.closed == "Always open":
        selected_closed_days = ['Always open']
    else:
        selected_closed_days = cafe.closed.split()
    edit_form = Cafeform(
        cafe = cafe.cafe,
        city = cafe.city,
        location = cafe.location,
        open_hours = cafe.open_hours,
        closed = selected_closed_days,
        sweets = cafe.sweets,
        coffee = cafe.coffee,
        wifi = cafe.wifi,
        power = cafe.power
    )
    if edit_form.validate_on_submit():
        cafe.cafe = edit_form.cafe.data
        cafe.city = edit_form.city.data
        cafe.location = edit_form.location.data
        cafe.open_hours = edit_form.open_hours.data
        cafe.closed = ' '.join(edit_form.closed.data)
        cafe.sweets = edit_form.sweets.data
        cafe.coffee = edit_form.coffee.data
        cafe.wifi = edit_form.wifi.data
        cafe.power = edit_form.power.data
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('edit.html', form=edit_form)


@app.route('/delete')
@login_required
def delete():
    if not current_user.is_admin:
        abort(403)

    cafe_id = request.args.get('id')
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('cafes'))


if __name__ == '__main__':
    app.run(debug=True)
