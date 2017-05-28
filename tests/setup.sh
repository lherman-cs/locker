#!/bin/bash

# Only support debian systems
DEPENDENCIES=(build-essential libssl-dev libffi-dev python3-dev)

sudo apt-get install ${DEPENDENCIES[@]}
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt

echo "Exporting path to ${HOME}/.bashrc"
echo "export PATH=\$PATH:$(pwd)" >> ${HOME}/.bashrc
source ${HOME}/.bashrc

echo "Creating executable file at $(pwd)/locker"
echo "#!/bin/bash" > locker
echo "" >> locker
echo "$(pwd)/env/bin/python3 $(pwd)/main.py \$@" >> locker
chmod +x locker
