from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm
from markupsafe import escape
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import logging
from logging.handlers import RotatingFileHandler
app = Flask(__name__)

db = SQLAlchemy()
bcrypt = Bcrypt()

handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

csrf = CSRFProtect(app)  # Enable CSRF Protection

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///firstapp.db"
app.config['SECRET_KEY'] = 'yoursecretkey'  # Required for Flask-WTF
app.config['SESSION_COOKIE_SECURE'] = True       # Cookies sent only over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True     # JavaScript can't access cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'    # CSRF prevention on cross-site requests
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 min session expiry

with app.app_context():
   db=SQLAlchemy(app)

#now making class to define structure of our db
class FirstApp(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"{self.sno} - {self.fname}"
    
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = RegistrationForm()
    session.permanent = True
    if form.validate_on_submit():
        fname = escape(form.fname.data)
        lname = escape(form.lname.data)
        email = escape(form.email.data)
         # Hash the password
        raw_password = escape(form.password.data)
        hashed_password = bcrypt.generate_password_hash(raw_password).decode('utf-8')
    
     # Store the hashed password
        firstapp = FirstApp(fname=fname, lname=lname, email=email, password=hashed_password)
        db.session.add(firstapp)
        db.session.commit()
        flash("Record added successfully!", "success")
    allpeople = db.session.execute(db.select(FirstApp)).scalars().all()
    return render_template('index.html', allpeople=allpeople, form=form)

    # return 'Hello, World!'

@app.route('/delete/<int:sno>')
def delete(sno):
    # first fetching the record with sno
    allpeople = db.session.execute(db.select(FirstApp).filter_by(sno=sno)).scalar_one_or_none()
    # now deleting the record
    if allpeople:
        db.session.delete(allpeople)
        db.session.commit()
        flash("Record deleted successfully!", "success")

    return redirect("/")

@app.route('/update/<int:sno>',methods = ['GET','POST'])
def update(sno):
    #first fetching the record with sno to be updated
    allpeople = db.session.execute(db.select(FirstApp).filter_by(sno=sno)).scalar_one_or_none()


    if request.method=='POST':
    #check if form field exists 
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        if fname and lname and email:
           #create and commit new record to the database
           allpeople.fname = escape(fname)
           allpeople.lname = escape(lname)
           allpeople.email = escape(email)
           db.session.add(allpeople)
           db.session.commit()
           flash("Record updated successfully!", "success")
           return redirect("/")  # Redirect to homepage after update


    return render_template('update.html',allpeople=allpeople)
# Handle 404 - Page Not Found
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Handle 500 - Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    # You can log the error here if needed (optional)
    return render_template('500.html'), 500

@app.route('/cause_error')
def cause_error():
    1 / 0  # This will cause a 500 Internal Server Error

@app.route("/home")
def home():
   return "welcome to the home page"
#writing main function
if __name__ == "__main__":
  app.run(debug=True)
