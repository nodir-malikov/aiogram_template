# aiogram_template

### About

Inspired by [Tishka17&#39;s tgbot_template](https://github.com/Tishka17/tgbot_template) and customized with some useful things.

Simple template for bots written on [aiogram](https://github.com/aiogram/aiogram).

### Setting up

#### System dependencies

* Python 3.9+
* Redis (if you set `use_redis = true` in **bot.ini**)

#### Preparations

* Clone this repo via `https://github.com/nodir-malikov/aiogram_template.git`

Without Poetry:

* Create virtual environment: `python -m venv venv`
* Make **venv** your source: `source ./venv/bin/activate` (Linux) or `.\venv\Scripts\activate (Windows)`
* Install requirements: `pip install -r requirements.txt`

With Poetry:

* Just run `poetry install` (if you haven't installed poetry yet, you can find instructions **[here](https://python-poetry.org/docs/)**)

### Deployment

* Copy **bot.ini.example** to **bot.ini** and set your variables.

Without Systemd:

* Run bot: `python bot.py`

With Systemd:

* Copy systemd config to systemd system folder with: `sudo cp systemd/yourbotname.service.example /etc/systemd/system/mynewbot.service` "mynewbot" - you can change to any name.
* Open config and reconfigure with your parameters: `sudo nano /etc/systemd/system/mynewbot.service`
* Reload systemd daemon with: `sudo systemctl daemon-reload`
* Start your bot service with: `sudo systemctl start mynewbot.service`

### Useful

**Aiogram**

* Docs: https://docs.aiogram.dev/en/latest/
* Community: https://t.me/aiogram
* Source code: https://github.com/aiogram/aiogram

**Test bot**: https://t.me/aiogram_template_bot
