from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, EmailField,FileField
from wtforms.validators import DataRequired, Length, Email


class RejoindreForm(FlaskForm):
    firstname = StringField(label=('Prénom'), validators=[DataRequired(),Length(min=2, max=30)])
    lastname = StringField(label=('Nom'), validators=[DataRequired(),Length(min=2, max=30)])
    phonenumber = StringField(label=('Téléphone'),validators=[Length(min=10, max=10)])
    email = EmailField(label=('Email'),validators=[DataRequired(), Email()])
    file = FileField(label=('Pièce Jointe'),validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField(label=('Envoyer'))