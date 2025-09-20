@echo off
echo Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

echo Executando o script...
python main.py

pause