from flask import (render_template, url_for, flash,
                   redirect, Blueprint,g)
from flask_mail import Message
from medeo import mail
from medeo.rejoindre.forms import RejoindreForm
import os

rejoindre = Blueprint('rejoindre', __name__,url_prefix='/<lang_code>')


@rejoindre.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@rejoindre.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

@rejoindre.route("/cabinet_nousrejoindre", methods=['GET','POST'])
def rejoigneznous():
    print(os.environ.get('CAPTCHA_PUBLIC_KEY'))
    form=RejoindreForm()
    if form.validate_on_submit():
        with mail.connect() as conn:

            # Mail sent to medeo to get info
            msg1 = Message("CV - SITES",
                        sender='contact@medeo-partners.com',
                        recipients=["contact@medeo-partners.com"])

            msg1.body = """
            Hello Team,
            You just received a contact form.
            Firstname: {}
            Lastname: {}
            Phonenumber:{}
            Email: {}
            """.format(form.firstname.data,form.lastname.data,form.phonenumber.data,form.email.data)
            msg1.attach(
            form.file.data.filename,
            'application/octect-stream',
            form.file.data.read())
            conn.send(msg1)

            # # Mail sent to the new client
            # msg2 = Message("Merci pour votre candidature",
            #     sender='contact@medeo-partners.com',
            #     recipients=[form.email.data])
            # msg2.body="""
            # Bonjour {} {},

            # MEDEO PARTNERS tiens à vous remercier pour votre intérêt pour nos services. Nous avons bien reçu votre candidature spontanée via notre formulaire de contact sur notre site internet et nous vous en remercions.

            # Nous reviendrons vers vous pour organiser un appel téléphonique ou une réunion en personne.


            # Cordialement,

            # MEDEO TEAM
            # """.format(form.firstname.data,form.lastname.data)
            # conn.send(msg2)

            flash('Votre message a été delivré à la MEDEO Team !', 'success')
            return redirect(url_for('main.home'))
    flash('Assurez-vous de cocher sur le reCaptcha !', 'warning')
    return render_template('cabinet/cabinet_nousrejoindre.html',title='Contact',form=form)

    