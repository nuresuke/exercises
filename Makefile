VENV?=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

install: poke
	$(PIP) install -r requirements.txt

initdb:
	sqlite3 DB/sqlite/pokemon.sqlite3 < DB/sqlite/pokemon.sql

setup: install initdb
	echo "Setup complete!"

#make setupのコマンドを打つこと！