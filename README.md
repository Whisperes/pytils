# pytils
Utils for data python project



#create venv
python -m venv env
env\Scripts\activate.bat

pip3 freeze > requirements.txt

#packages
Dynaconf
dynaconf init -f toml


profilehooks

#Distribution
python -m pip install --user --upgrade setuptools wheel
python -m pip install wheel
python setup.py sdist bdist_wheel

