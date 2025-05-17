import argparse
import json
import os
import time

import readline
import requests


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_agent(text, speed=.0003):
    print(f'{bcolors.OKGREEN}Chat Agent: ', end='')
    for i, char in enumerate(text):
        print(char, end='', flush=True)
        if char in ['.', ',', '?', '-', ':', '!']:
            if i >= len(text) - 2:
                time.sleep(speed * 10)
            elif text[i+1] == ' ':
                # Only pause when punctation is followed by a space.
                time.sleep(speed * 10)
            else:
                time.sleep(speed)
        else:
            time.sleep(speed)
    print(f'{bcolors.ENDC}')

def slow_print(text, speed=.003):
    for char in text:
        print(char, end='', flush=True)
        if char in ['.', ',', '?', '-', ':', '!']:
            time.sleep(speed * 10)
        else:
            time.sleep(speed)

def input_user(speed=.003):
    user_input = input(f'{bcolors.OKBLUE}User: ')
    print(bcolors.ENDC, end='')
    time.sleep(speed)
    return user_input

def make_json_request(data):
    return json.dumps(data)


def reset_chat_sessions(url):
    header = {'Content-Type': 'application/json'}
    resp = requests.post(os.path.join(url, 'reset'), json={'chat_id':'all'}, headers=header)
    print('Reset request:')
    print(f'Code: {resp.status_code} Message: {resp.content.decode("utf-8") }')

# Begin Chat script
arg_parser =argparse.ArgumentParser()
arg_parser.add_argument('-e', '--env', default='local')
args = arg_parser.parse_args()

if args.env.lower() in ['d', 'dev', 'development']:
    url = 'http://testmlearn01:6005/chat'
    print('Using development endpoint')
elif args.env.lower() in ['m']:
    url = 'http://mpamuw101:6005/chat'
    print("Using model office endpoint")
elif args.env.lower() in ['l', 'local']:
    url = 'http://127.0.0.1:5000/chat'
    print('Using local endpoint')
else:
    print(f'Argument {args.env} not understood. Using local URL.')
    url = 'http://127.0.0.1:5000/chat'


# Reset session object
# reset_chat_sessions(url)

header = {'Content-Type': 'application/json'}
cookies = None
user_input = ''

readline.set_history_length(100)
history_path = os.path.join(os.path.dirname(__file__), '.demo-cache/.history.txt')
if not os.path.isdir(os.path.dirname(history_path)):
    os.makedirs(os.path.dirname(history_path), exist_ok=True)

if os.path.isfile(history_path):
    readline.read_history_file(history_path)

# Initalize chat with GET request
resp = requests.get(url)
print('Initial response recieved.')
print(resp.content)
resp_body = json.loads(resp.content)
cookies = resp.cookies

message = resp_body['chat']
chat_id = resp_body['chat_id']

# Display initial message
print_agent(message)
user_input = input_user()


while user_input != 'q':
    
    json_request = make_json_request({'chat': user_input, 'chat_id': chat_id})
    try:
        resp = requests.post(os.path.join(url, chat_id), data=json_request, headers=header, cookies=cookies)
        resp_body = json.loads(resp.content)
        message = resp_body['chat']
        # message = resp.content.decode("utf-8") 
        print_agent(message)

        user_input = input_user()

    except requests.exceptions.ConnectionError:
        print('Connection ended, most likely a restart')
        time.sleep(5)
        print('Do you want to resubmit? [y]/n')
        user_input = input_user()
        if user_input == 'y':
            break
        # prev_input = readline.get_history_item(-1)
        # readline.add_history(user_input)
        # user_input = prev_input
    except KeyboardInterrupt:
        print(f'\n{bcolors.ENDC}Goodbye!')
        break

readline.write_history_file(history_path)