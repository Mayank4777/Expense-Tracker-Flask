from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
import os

app=Flask(__name__)
app.secret_key="mayank12345"

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class Records(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    desc=db.Column(db.String(100))
    inc_exp=db.Column(db.String(100))
    amount=db.Column(db.Integer)

    user_id=db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)

class Users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    u_name=db.Column(db.String(100),nullable=False)
    u_password=db.Column(db.String(100))
    records=db.relationship('Records',backref='user',lazy=True)

with app.app_context():
    if not os.path.exists('data.db'):
        db.create_all()

def calculate_total():
    # session['user_id']=Users.id
    all_records=Records.query.filter_by(user_id=session['user_id']).all()
    total=0
    for r in all_records:
        if r.inc_exp=="expense":
            total -= r.amount
        else:
            total += r.amount

    return total

@app.route("/")
def register():
    return render_template('register.html')

@app.route("/registerdetails",methods=['GET','POST'])
def registersubmit():
    u_name=request.form['username']
    password=request.form['password']

    userexist=Users.query.filter_by(u_name=u_name).all()
    
    if userexist:
        flash("User already exists. Please Login.", "error")
        return redirect(url_for("login"))
    else:
        user=Users(u_name=u_name,u_password=password)
        db.session.add(user)
        db.session.commit()
        session['user_id']=user.id
        return redirect(url_for("index"))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logincheck',methods=['POST'])
def logincheck():
    u_name=request.form['username']
    password=request.form['password']

    user=Users.query.filter_by(u_name=u_name).first()
    # existpass=Users.query.filter_by(password=password)

    if not user:
        flash("User not found Please try again.", "error")
        return redirect(url_for("register"))

    if password==user.u_password:
        session['user_id']=user.id
        return redirect(url_for("index"))
    else:
        flash("Incorrect password. Please try again.", "error")
        return redirect(url_for("login"))

@app.route("/index")
def index():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    all_records=Records.query.filter_by(user_id=session['user_id']).all()
    total=calculate_total()
    return render_template('index.html',records=all_records,total=total)

@app.route("/submit",methods=['POST'])
def submit():
    desc=request.form['desc']
    inc_exp=request.form['inc_exp']
    amount=int(request.form['amount'])
    
    new_record=Records(desc=desc,inc_exp=inc_exp,amount=amount,user_id=session['user_id'])
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/delete/<int:id>')
def delete(id):
    record=Records.query.get(id)
    
    db.session.delete(record)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit(id):
    record=Records.query.get(id)
    return render_template("edit.html",record=record)

@app.route('/updatepage/<int:id>',methods=['POST'])
def updatepage(id):
    record=Records.query.get(id)
    total=calculate_total()

    record.desc=request.form['desc']
    record.inc_exp=request.form['inc_exp']
    record.amount=request.form['amount']
    db.session.commit()

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True)