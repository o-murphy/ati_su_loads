loads scrapper for ati.su
-------------------------

v1.0.1a0 (Python 3.8+)

**Instalation**
```commandline
git clone https://github.com/o-murphy/ati_su_loads
cd ati_su_loads
python venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp example-config.toml config.toml
```
Config edit:
```commandline
vim config.toml
```
Run:
```commandline
python main.py
```
