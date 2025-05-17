### Run React
```bash
cd fp-react
yarn start
```
If this fails, most likely missing recent packages. Try `yarn install`.

## Python Services
Make sure you activate fp-assist conda environment before running the following python services. 

### Run FP Assistant Chat 
```bash
cd fp-assistant-chat
export FLASK_APP=application
export FLASK_ENV=development
flask run 
```

### Run FP Assistant Analysis (+ Data Manager)
```bash
cd fp-assistant
PYTHONPATH="app" uvicorn app.main:api --port 5001
```
