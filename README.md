# TEStribute
Task distribution logic for use in proTES repo

## Installation Instructions : 
```bash
git clone git@github.com:elixir-europe/TEStribute.git
cd TEStribute
virtualenv -p `which python3` venv
source venv/bin/activate
pip install -r requirements.txt
```

## Current Functionality

The ```main``` defined in the ```__init__``` defines a test case for function ```rank_services``` which defines the 
function to return a dict of ranked TES & DRS services for each input task.
The service debug messages can be viewed in the tes_log.log file created in the log folder.
