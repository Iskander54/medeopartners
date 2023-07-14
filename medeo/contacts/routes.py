from flask import (render_template, url_for, flash,
                   redirect, Blueprint,g)
from flask_mail import Message
from medeo import mail
from flask_babel import _,refresh
from medeo.contacts.forms import ContactForm

contacts = Blueprint('contacts', __name__,url_prefix='/<lang_code>')

@contacts.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@contacts.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@contacts.route("/nouscontacter", methods=['GET','POST'])
def contact():
    form=ContactForm()
    if form.validate_on_submit():
        with mail.connect() as conn:
            print(conn)
            # Mail sent to medeo to get info
            msg1 = Message(form.subject.data,
                        sender='alex-kevin.loembe@medeo-tax.com',
                        recipients=["a.loembe@prometheuscomputing.com"])

            msg1.body = """
            Hello Team,
            You just received a contact form.
            Firstname: {}
            Lastname: {}
            Phonenumber:{}
            Email: {}
            Message: {}
            """.format(form.firstname.data,form.lastname.data,form.phonenumber.data,form.email.data,form.content.data)
            conn.send(msg1)
            flash('Votre message a été delivré à la MEDEO Team !', 'success')
            return redirect(url_for('main.home'))
    return render_template('nouscontacter.html',title='Contact',form=form)

    