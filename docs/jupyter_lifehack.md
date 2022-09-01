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

#Start jupyter on LAN
    jupyter notebook --ip /YOUR IP/ --port 8888 

#Start jupyter with venv
    conda activate TestLibraries    
