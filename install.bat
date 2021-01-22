REM
python -m pip install --upgrade pip 
pip install virtualenv 
pip install virtualenvwrapper-win 
mkvirtualenv virt-ihm-master 
setprojectdir . 
workon virt-ihm-master 
pip install -r requirements.txt