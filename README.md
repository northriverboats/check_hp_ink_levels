Check HP Ink Levels
===================
This application will check the current ink cartridge levels on one
HP Designjet Z5200 specificd by `URL` and email the list `MAIL_TO` 

Installing Dependencies
===============================
```
python -m pip install pip --upgrade
pip install git+https://github.com/northriverboats/emailer.git
pip install git+https://github.com/northriverboats/mysql-tunnel.git
pip install -r requirements.txt
```

Buidling Executable
===============================
Initial
```
pyinstaller --onefile hulls2site.py
```
Shorthand
```
pyinsaller hulls2site.spec
```

