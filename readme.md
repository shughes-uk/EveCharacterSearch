# Eve Character Search

![preview](https://cloud.githubusercontent.com/assets/546891/17384760/d1005850-59a3-11e6-93e0-8efb915ef035.png)

Eve Character Search is at the front a dynamic webpage that allows searching a live database of eve online character sales from the Character Bazaar Forums, and a scraping tool that monitors the forums and scrapes detailed information on the character for sale into a database for the webpage.

ECS leverages [Django][django] and [BeautifulSoup][beautifulsoup].

## Getting Started

### OS X

Make sure Xcode Command Line Tools installed and up to date.

```shell
$ xcode-select --install
```

Use [Homebrew](https://brew.sh) to install `pyenv` and `virtualwrapper`.

```shell
$ brew install pyenv-virtualenvwrapper
```

Use `pyenv` to install a python to use with `virtualwrapper`.

```shell
$ pyenv install 2.7.12
$ pyenv global 2.7.12
```

Configure your shell session for use with `virtualenvwrapper`.

```shell
$ export PYENV_ROOT=/usr/local/var/pyenv
$ eval "$(pyenv init -)"
$ pyenv virtualenvwrapper
```

Create a new `virtualenv` for `EveCharacterSearch`.

```shell
mkvirtualenv -r requirements.txt eve
workon eve
```

Start a local instance of `EveCharacterSearch`.

```shell
cp ./evecharsearch/settings_example.py ./evecharsearch/settings.py
python manage.py makemigrations
python manage.py migrate
python manage.py update_api
python manage.py scrape_threads # use --pages to scrap more than 1 page
python manage.py runserver
```

---

[MIT][mit] © [shughes-uk][author] et [al][contributors]

[mit]:              http://opensource.org/licenses/MIT
[author]:           http://github.com/shughes-uk
[contributors]:     https://github.com/shughes-uk/EveCharacterSearch/graphs/contributors
[django]:           https://github.com/django/django
[beautifulsoup]:    https://www.crummy.com/software/BeautifulSoup/
