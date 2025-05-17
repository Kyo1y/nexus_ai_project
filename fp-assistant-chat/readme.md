# FP Assistant Chat 
This project contains the logic to allow a user to ask questions using natural language and translate them into queries to be sent to an external data service.

# Set Up instructions.
This project uses **Python 3.8.16**. To begin, make a conda enviornment.

```bash
conda create -n fp-assist Python=3.8.16
```

Activate the enviornment and install python packages using pip
```bash
conda activate fp-assist
pip install -r appplication/requirements.txt
```

# Running project
To run the project in the terminal,
```bash
export FLASK_APP=application
export FLASK_ENV=development
flask run
```

To run using VS Code debugger, set up the file `.vscode/launch.json` to be configured as follows.
```json
{
    "name": "Python: Flask App",
    "type": "python",
    "request": "launch",
    "module": "flask",
    "env": {
        "FLASK_APP": "app.py",
        "FLASK_DEBUG": "1",
        "FLASK_ENV": "development",
        "OPENAI_API_KEY": "<openai-api-key>"
    },
    "args": [
        "run",
        "--no-debugger",
        "--no-reload"
    ],
    "jinja": true,
    "justMyCode": true,
    "cwd": "${workspaceFolder}/application"
}
```

# Project Organization
At the top level, there are 3 main directories. `application/` contains all the source code for the service. `scripts/` contains helpful scripts to help with development. `tests/` contains all the tests for the service.

## Design
The goal of the project is to have modules that handle different components of the service pipeline. When developing new modules, the goal should be to keep them as indepndent as possible.

## Import files and modules
- `application.chat.routes.py`: sets up routes for incoming HTTP calls to chat endpoints and passes relevant information to chat controller.
- `application.chat.manager.py`: controller for chat application. Contains all the logic for creating a new chat and continuing an existing one. 
- `application.chat.outputter`: manages language to be returned to the user during the chat.
- `application.config`: manages configurations for the app. Should have a single instatiated object that is shared across modules
- `application.models`: base classes for different data objects used in the app. All logic here should be general and not contain any business rules
- `application.openai_manager`: handles making calls to OpenAI API.
- `application.querier`: creates object use to store query parameters that will be used to request data. This module should translate input to a query object, not make the request itself.
- `application.requestor`: sets up connections to query data based on query object. This is where request to data API should be set up and managed.
- `application.sessions:` tracks the interaction the user makes while chatting.
- `application.utils`: collection of utility functions that are reused. Aim is to provide function to repetative and common tasks that are not related to business logic. For example, reading and writing standard files, converting datetime to stings, etc.
- `application.viewer`: UI for interacting with service.

# Testing
Testing is managed using the [pytest](https://docs.pytest.org/en/7.4.x/) framework. To run tests, use the command:
```bash
pytest tests/
```
To get more information, there are extensions for generating an HTML report as well as a CSV. These can be made by using the following command:
```bash
pytest tests/ --html=${html_report_name} --self-contained-html --csv=${csv_report_name}
```

## Test coverage
To assess testing coverage, the python pacakge [coverage.py](https://coverage.readthedocs.io/en/7.4.1/) can be used in conjunction with pytest.

```
coverage run -m pytest tests/
```
