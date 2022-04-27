Check HP Ink Levels
===============================
This application will check the current ink cartridge levels on one
HP Designjet Z5200 specified by `URL` and email the list `MAIL_TO` 

Installing Dependencies
===============================
```
python -m pip install pip --upgrade
pip install git+https://github.com/northriverboats/emailer.git
pip install -r requirements.txt

cp env.sample .env
```

Buidling Executable
===============================
Initial
```
pyinstaller --onefile check_hp_ink_levels.py
```
Shorthand
```
pyinsaller check_hp_ink_levels.spec
```

Command Line Options
===============================
