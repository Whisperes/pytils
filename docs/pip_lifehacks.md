# PIP lifehacks

## import without SSL check
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org /YOUR LIBRARY/

## import from github
pip install git+https://github.com/Whisperes/pytils.git

## freeze all library requirements
pip3 freeze > requirements.txt

## Distribution package
python -m pip install --user --upgrade setuptools wheel
python -m pip install wheel
python setup.py sdist bdist_wheel


#Venv
python -m venv env
env\Scripts\activate.bat


