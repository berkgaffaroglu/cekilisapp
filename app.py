from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email,ValidationError
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bLq6HxQQ0r9bFnqm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class Katilan(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    isim = db.Column(db.String(20), nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)  
    katilmanedeni = db.Column(db.Text(), nullable=False) 
    katilmatarihi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Katilan('{self.isim}', '{self.email}', '{self.katilmatarihi}')"

class KatilmaFormu(FlaskForm):  
    email = StringField('Email', validators=[DataRequired(), Email()])
    isim = StringField('Isim', validators=[DataRequired(), Length(min=4, max=50)])
    katilmanedeni = TextAreaField('Katilma Nedeni (en az 30 karakter)', validators=[DataRequired(), Length(min=30, max=1000)])
    submit = SubmitField('Katıl')

    def validate_email(self, email):
        user = Katilan.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-mail kullanılmış. Lütfen başka bir e-mail girin.')

def cekilisTimer():
    tumkatilanlar = Katilan.query.all()
    katilanlarList = []
    for i in tumkatilanlar:
        katilanlarList.append(i.katilmatarihi)
    zamanaGoreKatilanlar = sorted(katilanlarList)
    ilkkatilan = zamanaGoreKatilanlar[0]
    cekilisBitisZamani = ilkkatilan + datetime.timedelta(minutes=3)
    return cekilisBitisZamani


@app.route('/')
@app.route('/anasayfa')
def anasayfa():
    cekilisBitisZamani = cekilisTimer()
    katilanlar = Katilan.query.all()
    return render_template('index.html', katilanlar=katilanlar, deadline = cekilisBitisZamani)
@app.route('/katil',methods=['GET','POST'])
def katil():
    form = KatilmaFormu()
    if form.validate_on_submit():
        katilanemail = form.email.data
        katilanisim = form.isim.data
        katilanneden = form.katilmanedeni.data
        katilan = Katilan(isim=katilanisim, email=katilanemail, katilmanedeni=katilanneden)
        db.session.add(katilan)
        db.session.commit()
        return redirect('anasayfa')
    return render_template('katil.html', title="Katıl!", form=form)


if __name__ == "__main__":
    app.run(debug=True)

