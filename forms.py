from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, FloatField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class InputForm(FlaskForm):
    stock = StringField('Enter Stock Symbol:', validators=[DataRequired()])
    submit_mlr = SubmitField('Submit')

class LongForm(FlaskForm):
    volume = FloatField('Enter Daily Volume:', validators=[DataRequired()])
    rsi = FloatField('Enter RSI:', validators=[DataRequired()])
    sma = FloatField('Enter SMA:', validators=[DataRequired()])
    macd = FloatField('Enter MACD:', validators=[DataRequired()])
    rmb = FloatField('Enter Middle BBand:', validators=[DataRequired()])
    rlb = FloatField('Enter Lower BBand:', validators=[DataRequired()])
    rub = FloatField('Enter Upper BBand:', validators=[DataRequired()])
    submit_automl = SubmitField('Submit')
