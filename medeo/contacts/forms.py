from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Length, Email


class ContactForm(FlaskForm):
    firstname = StringField(label=('Prénom'), validators=[DataRequired(),Length(min=2, max=30)])
    lastname = StringField(label=('Nom'), validators=[DataRequired(),Length(min=2, max=30)])
    phonenumber = StringField(label=('Téléphone'),validators=[Length(min=10, max=10)])
    email = EmailField(label=('Email'),validators=[DataRequired(), Email()])
    subject = StringField(label=('Sujet'),validators=[DataRequired(),Length(min=4, max=50)])
    content = TextAreaField(label=('Message'), validators=[DataRequired(),Length(min=10, max=200)])
    recaptcha = RecaptchaField()
    submit = SubmitField(label=('Envoyer'))