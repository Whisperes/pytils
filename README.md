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



#Hide code in Jupyter
from IPython.display import HTML
HTML('''<script>
code_show=false; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit" value="On/Off отображение кода."></form>''')

#Anchors
[Тотальная доходность портфеля во времени](#first-bullet)