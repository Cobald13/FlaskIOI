# Flask spletna aplikacija - backend

Flask aplikacija skrbi za backend - razpoznava slik, usmerjanje po spletni strani, prikazovanje slik in videov.
Ker se v flask aplikaciji izvajajo modeli strojnega učenja za razpoznavo slik, aplikacije za razliko od React frontenda ni bilo mogoče gostovati na brezplačni različici platforme Render.
Zato je potrebno lokalno izvajanje na lokalni napravi in potem t.i. port forwarding, ki omogoča, da je backend aplikacija dostopna iz zunanjega spleta.

## Ročno poganjanje aplikacije
Ročno poganjanje backend aplikacije zahteva več korakov in določene sistemske zahteve, zato odsvetujemo, da jo poganjate na lastni napravi. Namesto tega bomo poskrbeli, da se bo backend aplikacija v prihodnjih nekaj tednih izvajala stabilno na eni od naših naprav. Za omogočanje dostopa bomo uporabili orodje ngrok, ki omogoča t.i. port forwarding. Tako bo aplikacija dostopna od koder koli, podobno kot če bi bila gostovana na platformi, kot je Render.

## Ročno poganjanje aplikacije - nadaljevanje

Če vseeno želite backend aplikacijo namestiti in pognati lokalno, sledite naslednjim korakom.

### Predpogoji
Namestite Python (3.8 ali novejša različica): Prenesi Python.
Prepričajte se, da imate nameščen pip (upravitelj Python paketov).
Po želji ustvarite virtualno okolje, da se izognete konfliktom z globalno nameščenimi paketi.
Namestitev
#### 1. Kloniranje repozitorija
Klonirajte projekt na svoj računalnik:

`git clone <repozitorij-url>`\
`cd backend`\

#### 2. Nastavite virtualno okolje (neobvezno)
Ustvarite in aktivirajte virtualno okolje:

`# Ustvarite virtualno okolje`\
`python -m venv venv`

`# Aktivirajte virtualno okolje`\
`# Na Windows:`\
`venv\Scripts\activate`\
`# Na macOS/Linux:`\
`source venv/bin/activate`\

#### 3. Namestite odvisnosti
Namestite zahtevane Python pakete:

`pip install -r requirements.txt`\

#### 4. Preverite model datoteko
Prepričajte se, da datoteka painting_recognition_model.h5 obstaja v mapi backend. Če je ni, jo prenesite z uporabo `python app.py`, ki med drugim prenese ML model.

Zagon aplikacije\
Zaženite Flask aplikacijo:

`python app.py`\

Če je vse pravilno nastavljeno, boste videli naslednje sporočilo:

`Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`\

Sedaj lahko poženete lokalno React aplikacijo z `npm start` in lokalno poženete spletno aplikacijo na [http://localhost:3000](http://localhost:3000).
