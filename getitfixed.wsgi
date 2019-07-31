python_home = '[DIR]/.build/venv'
activate_this = python_home + '/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

from pyramid.paster import get_app, setup_logging
ini_path = '[DIR]/production.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
