from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError , Length


class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Submit')

    # Custom Validator for SQL Injection / XSS prevention
    def validate_fname(self, fname):
        if not fname.data.isalnum():
            raise ValidationError('First Name can only contain letters and numbers.')

    def validate_lname(self, lname):
        if not lname.data.isalnum():
            raise ValidationError('Last Name can only contain letters and numbers.')

    def validate_email(self, email):
        if "@" not in email.data or "." not in email.data:
            raise ValidationError('Invalid email address format.')
