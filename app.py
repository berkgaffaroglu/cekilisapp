from flask import Flask, render_template, redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField,IntegerField
import random
from wtforms.validators import DataRequired, Length, Email,ValidationError
from datetime import datetime,timedelta
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bLq6HxQQ0r9bFnqm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class Katilan(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    isim = db.Column(db.String(40), nullable=False)  
    email = db.Column(db.String(120), nullable=False)  
    katilmanedeni = db.Column(db.Text(), nullable=False) 
    katilmatarihi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Katilan('{self.isim}', '{self.email}', '{self.katilmatarihi}')"

class Kazanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    katilmanedeni = db.Column(db.Text(), nullable=False)

class KatilmaFormu(FlaskForm):  
    email = StringField('Email', validators=[DataRequired(), Length(min=4, max=100)])
    isim = StringField('Isim', validators=[DataRequired(), Length(min=4, max=50)])
    katilmanedeni = TextAreaField('Katilma Nedeni (en az 10, en çok 30 karakter)', validators=[DataRequired(), Length(min=10, max=30)])
    submit = SubmitField('Katıl')
    
class KisiOlusturmaFormu(FlaskForm):  
    kisi_sayisi = IntegerField('Rastgele Kişi Sayısı:')
    submit = SubmitField('Oluştur')


def cekilisTimer():
    # Katılan tüm kişileri çek
    tumkatilanlar = Katilan.query.all()
    if len(tumkatilanlar) > 0: 
        katilanlarList = []
        for i in tumkatilanlar:
            katilanlarList.append(i.katilmatarihi)
        zamanaGoreKatilanlar = sorted(katilanlarList)
        ilkkatilan = zamanaGoreKatilanlar[0]
        cekilisBitisZamani = ilkkatilan + timedelta(seconds=30)
        return cekilisBitisZamani
    else:
        cekilisBitisZamani = datetime(4000,12,25,10,50,5,10)
        return cekilisBitisZamani


def kazananiBelirle():
    deadline = cekilisTimer()
    kazananlar = Kazanan.query.all()
    # Şu anki zaman deadline'ı geçtiyse ve database'de kazanan yoksa devam et.
    if datetime.utcnow() > deadline:
        if(len(kazananlar) == 0):
            katilanlar = Katilan.query.all()
            # Katılanların sayısı 0 dan büyükse kazananları seç
            if len(katilanlar) != 0:
            
                # Katılanların sayısı 3'ten büyükse 3 tane kazanan seç.
                if len(katilanlar) > 3:
                    tumkazananlar = random.sample(katilanlar, 3)
                    for kazanan in tumkazananlar:
                        kazananKatilimci = Kazanan(email=kazanan.email, isim=kazanan.isim, katilmanedeni=kazanan.katilmanedeni)
                        db.session.add(kazananKatilimci)
                    db.session.commit()
                    return tumkazananlar
                # Katılanların sayısı 3'ten küçükse katılanların hepsini kazanan seç
                else:
                    tumkazananlar = katilanlar
                    for kazanan in tumkazananlar:
                        kazananKatilimci = Kazanan(email=kazanan.email, isim=kazanan.isim, katilmanedeni=kazanan.katilmanedeni)
                        db.session.add(kazananKatilimci)
                    db.session.commit()
                    return tumkazananlar
        
            
            else:
                notificationList = ['Katılan kimse olmadı..']
                return notificationList
        else:
            return kazananlar
    else:
        emptyList = list()
        return emptyList

def rastgeleKisiOlustur():
    rastgeleisimler = ['cem','haydar','hüseyin','ahmet','mehmet','yilmaz','corey','deniz','yunus','ece','kaya','sude']
    rastgelesayilar = ['123','321','45478','213123','54779']
    domainler = ['@yahoo.com','@gmail.com']
    katilmanedenleri = ['Bu çekilişte kazanan olmayı çok istiyorum. Umarım bu çekilişin kazananı ben olurum.','Bu çekilişe katılacağım için çok heyecanlıyım!','Artık bir çekilişin kazananı olmak istiyorum!','Kazandığımda ne yapacağımı gayet iyi biliyorum :)']

    isim = random.choice(rastgeleisimler)
    email = f'{isim}{random.choice(rastgelesayilar)}{random.choice(domainler)}'

    katilmanedeni = random.choice(katilmanedenleri)
    kisi = Katilan(isim=isim, email=email, katilmanedeni=katilmanedeni)
    return kisi
    
@app.route('/testkatilimciekle/<int:kisi_sayisi>')
def testkatilimci(kisi_sayisi):
    if kisi_sayisi > 100:
        kisi_sayisi = 100
    for i in range(kisi_sayisi):
        kisi = rastgeleKisiOlustur()
        db.session.add(kisi)
    db.session.commit()
    return redirect(url_for('anasayfa'))

      
     

  
        
    
@app.route('/', methods=['GET','POST'])
@app.route('/anasayfa',methods=['GET','POST'])
def anasayfa():
    deadline = cekilisTimer()
    katilanlar = Katilan.query.all()
    realityCheck = datetime.utcnow() + timedelta(days=9999)
    kazananList = kazananiBelirle()
    form = KisiOlusturmaFormu()
    if request.method == 'POST':
        kisi_sayisi = form.kisi_sayisi.data
        if not kisi_sayisi:
            kisi_sayisi = 20
        return redirect(url_for('testkatilimci', kisi_sayisi=kisi_sayisi))
    return render_template('index.html', katilanlar=katilanlar, deadline=deadline, now=datetime.utcnow(), realityCheck=realityCheck, kazananList=kazananList, form=form)


@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')



    


@app.route('/katil',methods=['GET','POST'])
def katil():
    form = KatilmaFormu()
    deadline = cekilisTimer()
    if form.validate_on_submit():
        katilanemail = form.email.data
        katilanisim = form.isim.data
        katilanneden = form.katilmanedeni.data
        katilan = Katilan(email=katilanemail, isim=katilanisim, katilmanedeni=katilanneden)
        db.session.add(katilan)
        db.session.commit()
        return redirect('anasayfa')
    return render_template('katil.html', title="Katıl!", form=form, deadline=deadline, now = datetime.utcnow())

@app.route('/reset',methods=['GET','POST'])
def reset():
    tumkazananlar = Kazanan.query.all()
    tumkatilanlar = Katilan.query.all()
    for kazanan in tumkazananlar:
        db.session.delete(kazanan)
    for katilan in tumkatilanlar:
        db.session.delete(katilan)
    db.session.commit()
    return redirect(url_for('anasayfa'))

if __name__ == "__main__":
    app.run()

