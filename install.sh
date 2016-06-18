cd src

cd cobwebs
sudo pip install -r requirements.txt
sudo python3 setup.py install
cd -

cd apiviewer
sudo pip install -r requirements.txt
sudo python3 setup.py install
cd -

cd dbdriver
sudo pip install -r requirements.txt
sudo python3 setup.py install
cd -

cd spider
sudo pip install -r requirements.txt
sudo python3 setup.py install
cd -

