from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Length, Email
from flask_babel import _, lazy_gettext as l


class ContactForm(FlaskForm):
    firstname = StringField(label=('Prénom'), validators=[DataRequired(), Length(
        min=2, max=30)], render_kw={"placeholder": _("PRÉNOM")})
    lastname = StringField(label=('Nom'), validators=[
                           DataRequired(), Length(min=2, max=30)], render_kw={"placeholder": _("NOM")})
    phonenumber = StringField(label=('Téléphone'), validators=[
                              Length(min=10, max=10)], render_kw={"placeholder": _("TÉLÉPHONE")})
    email = EmailField(label=('Email'), validators=[
                       DataRequired(), Email()], render_kw={"placeholder": _("E-MAIL")})
    subject = StringField(label=('Sujet'), validators=[
                          DataRequired(), Length(min=4, max=50)], render_kw={"placeholder": _("SUJET")})
    content = TextAreaField(label=('Message'), validators=[
                            DataRequired(), Length(min=10, max=200)], render_kw={"placeholder": _("MESSAGE")})
    recaptcha = RecaptchaField()
    submit = SubmitField(label=('Envoyer'))
