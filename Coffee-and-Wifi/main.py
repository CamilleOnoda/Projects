from flask import Flask, redirect, render_template, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, SubmitField, widgets
from wtforms.validators import DataRequired
import os


app = Flask(__name__)
Bootstrap5(app)
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['SECRET_KEY'] = SECRET_KEY


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coffee-wifi.db"
db = SQLAlchemy()
db.init_app(app)


Base = declarative_base()


class Cafeform(FlaskForm):
    cafe = StringField('Cafe', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    open_hours = StringField('Opening hours', validators=[DataRequired()])
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
    sweets = SelectField('Sweets', choices=[('🍩', '🍩'),
                                            ('🍩🍩', '🍩🍩'),
                                            ('🍩🍩🍩', '🍩🍩🍩'),
                                            ('🍩🍩🍩🍩', '🍩🍩🍩🍩🍩'),
                                            ('🍩🍩🍩🍩🍩', '🍩🍩🍩🍩🍩🍩')],
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
    power = SelectField('Power', choices=[('✘', '✘'), ('🔌', '🔌'),
                                          ('🔌🔌', '🔌🔌'),
                                          ('🔌🔌🔌', '🔌🔌🔌'),
                                          ('🔌🔌🔌🔌', '🔌🔌🔌🔌'),
                                          ('🔌🔌🔌🔌🔌', '🔌🔌🔌🔌🔌')],
                                          validators=[DataRequired()])
    submit = SubmitField("➕Add", validators=[DataRequired()])


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


with app.app_context():
    db.create_all()


# Flask routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/cafes')
def cafes():
    cafes_list = list(db.session.execute(db.select(Cafe).order_by(Cafe.city)).scalars())
    return render_template('cafes.html', cafes_list=cafes_list)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = Cafeform()
    if form.validate_on_submit():
        closed_days = ','.join(form.closed.data)
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


@app.route('/delete')
def delete():
    cafe_id = request.args.get('id')
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('cafes'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        cafe_id = request.form['id']
        cafe_to_edit = db.get_or_404(Cafe, cafe_id)
        cafe_to_edit.cafe = request.form["cafe"]
        cafe_to_edit.city = request.form["city"]
        cafe_to_edit.location = request.form["location"]
        cafe_to_edit.open_hours = request.form["open_hours"]
        cafe_to_edit.closed = ','.join(request.form.getlist("closed"))
        cafe_to_edit.sweets = request.form["sweets"]
        cafe_to_edit.coffee = request.form["coffee"]
        cafe_to_edit.wifi = request.form["wifi"]
        cafe_to_edit.power = request.form["power"]
        db.session.commit()
        return redirect(url_for('cafes'))
    cafe_id = request.args.get('id')
    cafe_selected = db.get_or_404(Cafe, cafe_id)
    return render_template('edit.html', cafe=cafe_selected)


if __name__ == '__main__':
    app.run(debug=True)
