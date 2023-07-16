# !/usr/bin/env python3
# coding:utf-8

import os
import time
from multiprocessing import Event, Queue, Process, Manager, Lock
from zipfile import ZipFile
import subprocess
import itertools
import string
import argparse


# ANSI ESCAPE SEQUENCES
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

RESET = '\033[0m'
UP = "\033[1A"
CLEAR = "\x1b[2K"

def wait(wait_time):
    return 0 if wait_time==None else float(wait_time[0])

def path_format(path):
    return (r'{}'.format(path)).replace('//', '/').replace(r'\\', '/')

def detail(help_detail):
    if help_detail == 'chars':
        print(
f"""
FORMAT: --chars {LIGHT_BLUE}[ALPHABET]{RESET} {LIGHT_GREEN}[LENGTH]{RESET} {LIGHT_CYAN}[PROCESS]{RESET}

+ {LIGHT_BLUE}[ALPHABET]{RESET} : Default type: all, letters, lowercase, uppercase, digits, punctuation or mutiple ones separated by comma (ex: digits,uppercase). Or you can pass your custom alphabet instead of using default one (ex: 12345abcd, XYZ!@#$)
+ {LIGHT_GREEN}[LENGTH]{RESET} : Format: START_LENGTH,STOP_LENGTH (ex: 3,8 means that the program will try to find the password whose length is from 3 to 8 letters)
+ {LIGHT_CYAN}[PROCESS]{RESET} : Number of processes to run in parallel (integer only)
"""
        )
    elif help_detail == 'list':
        print(
f"""
FORMAT: --list {LIGHT_BLUE}[TXT_FILE]{RESET} {LIGHT_GREEN}[PROCESS]{RESET}

+ {LIGHT_BLUE}[TXT_FILE]{RESET} : .txt file used for testing password
+ {LIGHT_GREEN}[PROCESS]{RESET} : Number of processes to run in parallel (integer only)
"""
        )
    else:
        return ''

def requirements(file, alphabet, length, process):
    check = True
    error = []

    for i in file:
        if path_format(i) != None and os.path.exists(path_format(i)) == False:
            check = False
            error.append(f"Error: No such file or directory: '{i}'")

    if int(process) > 10:
        check = False
        error.append('Error: Maximum of process is 10')

    if type_chars != None and type_lst != None:
        check = False
        error.append('Error: Choose "--chars" or "--list" only, not both!')
    
    if length[0] > length[1]:
        check = False
        error.append('Error: Minimum length is greater than maximum length')
    
    if check == False:
        for i in error:
            print(f'{RED}{i}{RESET}')
        raise SystemExit
    
def alphabet_format(alphabet):
    full = ''
    for i in alphabet.split(','):
        if ' ' in i:
            print(f'{RED}Error: Whitespace is not allowed in alphabet{RESET}')
            raise SystemExit

        if i == 'all':
            full += string.printable.strip()
        elif i == 'letters':
            full += string.ascii_letters
        elif i == 'lowercase':
            full += string.ascii_lowercase
        elif i == 'uppercase':
            full += string.ascii_uppercase
        elif i == 'digits':
            full += string.digits
        elif i == 'punctuation':
            full += string.punctuation
        else:
            full += i.strip()
    
    return full

def extract_format(file, pwd, wait_time):
    dep = path_format(file[0])
    des = '.'
    if len(file) == 2:
        des = path_format(file[1])
    elif len(file) > 2:
        print(f"{RED}Error: Expected 2 arguments{RESET}")
        raise SystemExit

    time.sleep(wait(wait_time))
    try:
        if '.zip' in dep:
            zip = ZipFile(dep, 'r')
            zip.extractall(
                path = des + '/' + dep[dep.rfind('/') + 1: ].replace('.zip','')+"_uncompressed", 
                pwd=pwd.encode('utf-8')
            )
            zip.close()
        elif '.rar' in dep:
            result = subprocess.run(['unrar', 'x', '-p' + pwd, dep, des], capture_output=True, text=True, check=False, input='y')
            if result.returncode == 11:
                # time.sleep(0.1) For lower CPU usage
                raise RuntimeError

    except TypeError:
        print(f"{RED}Error: No such file or directory: '{file}'{RESET}")
        raise SystemExit
    except FileExistsError:
        print(f"{RED}Error: File exists: '{file}'{RESET}")
        raise SystemExit


parser = argparse.ArgumentParser(description="Python password bruteforce program using multiprocessing module. Copyright © 2023 NautilusZ")
parser.add_argument('--detail', metavar='TYPE', type=str, help="Detailed instruction of 'chars' or 'list' option")
parser.add_argument('--file', metavar='', nargs='+', type=str, help="Supported extension: .rar, .zip")
parser.add_argument('--chars', metavar='', nargs='+', type=str, help="Character-based brute-force. use '--detail chars' for instruction")
parser.add_argument('--list', metavar='', nargs='+', type=str, help="List-based brute-force. use '--detail list' for instruction")
parser.add_argument('--include', metavar='WORD', type=str, help="Word to include in password string")
parser.add_argument('--log', metavar='', nargs='*', help='Log the previous tested cases (for --chars only)')
parser.add_argument('--wait', metavar='TIME', nargs=1, type=float, help='Time interval in seconds between each password trial (recommended for .rar)')
task_args = vars(parser.parse_args())

help_detail = task_args['detail']
file = task_args['file']
type_chars = task_args['chars']
type_lst = task_args['list']
word_include = task_args['include'].split(',') if task_args['include'] != None else None
log = task_args['log']
wait_time = task_args['wait']

alphabet = ''
length = []
num_parts = 0
part_size = 0
task_type = ''


if type_chars != None and type_lst == None:
    if len(type_chars) != 3:
        print(f'{RED}Error: Expected 3 arguments{RESET}')
        raise SystemExit
    else:
        task_type = 'chars'
        alphabet = alphabet_format(type_chars[0])
        length = [int(i) for i in type_chars[1].split(',')]
        num_parts = int(type_chars[2]) if int(type_chars[2]) < len(alphabet) else len(alphabet)
        part_size = len(alphabet) // num_parts

elif type_lst != None and type_chars == None:
    if len(type_lst) != 2:
        print(f'{RED}Error: Expected 2 arguments{RESET}')
        raise SystemExit
    else:
        task_type = 'list'
        if type_lst[0].endswith('.txt'):
            txt = open(type_lst[0], 'r', encoding='ISO-8859-1')
            lines = txt.readlines()

            num_parts = int(type_lst[1]) if int(type_lst[1]) < len(lines) else len(lines)
            part_size = len(lines) // num_parts

        else:
            print(f'{RED}Error: Must be a .txt file{RESET}')
            raise SystemExit
        
if (type_chars != None or type_lst != None) and file == None:
    print(f"{RED}Error: No such file or directory: '{file}'{RESET}")
    raise SystemExit
    
def chars_task(n, file, task_args, event, result_queue, shared_tasks, shared_total, shared_case, lock):
    if word_include != None:
        for part in task_args:
            part = [j.split(',') for j in part]
            for i in itertools.product(*part):
                shared_case.value += 1
                pwd = ''.join(i)
                shared_tasks[n] = f"{LIGHT_GRAY}Process_{n} : {RESET}{pwd}"
                try:
                    extract_format(file, pwd, wait_time)
                    result_queue.put(pwd)
                    event.set()
                    break
                except RuntimeError:
                    continue
    else:
        for i in itertools.product(*task_args):
            # lock.acquire()
            shared_case.value += 1
            pwd = ''.join(i)
            shared_tasks[n] = f"{LIGHT_GRAY}Process_{n} : {RESET}{pwd}"
            try:
                extract_format(file, pwd, wait_time)
                result_queue.put(pwd)
                event.set()
                break
            except RuntimeError:
                continue

    lock.acquire() # Avoid duplicating password among parallel processes
    shared_total.value += 1
    lock.release()

    return

def list_task(n, file, list_range, event, result_queue, shared_tasks, shared_total, shared_case, lock):
    rar = None  # Initialize rarfile.RarFile outside the loop
    for i in range(list_range[0], list_range[1]):
        lock.acquire()
        shared_case.value += 1
        pwd = lines[i].replace('\n', '')
        if rar is None:
            # Acquire the lock before creating the rarfile.RarFile instance
            shared_tasks[n] = f"{LIGHT_GRAY}Process_{n} : {RESET}{pwd}"
            try:
                extract_format(file, pwd, wait_time)
                result_queue.put(pwd)
                event.set()
                break  # Password found, terminate the loop
            except RuntimeError:
                continue
            finally:
                lock.release()

    if rar is not None:
        rar.close()
    
    shared_total.value += 1
    return

def print_tasks(shared_tasks, shared_case, total_cases, st):
    while True:
        delta = (time.time() - st)
        speed = round(shared_case.value//delta) if delta != 0 else 0
        print('\n'.join(shared_tasks))
        # print(f'{LIGHT_GRAY}Finished processes: {RESET}{shared_total.value}')
        print(f'{LIGHT_GRAY}Tested cases : {RESET}{shared_case.value}/{total_cases} ({speed} pwd/s)')
        print(f'{LIGHT_GRAY}Elapsed time : {RESET}' + '{:02.0f}:{:02.0f}:{:02.0f}:{:06.3f}'.format(delta//86400, (delta%86400)//3600, ((delta%86400)%3600)//60, round(((delta%86400)%3600)%60, 3)))
        print((UP + CLEAR)*(num_parts+2), end="")
        time.sleep(0.1) # Refresh rate

def check_finish(shared_total, num_parts, event):
    while True:
        if shared_total.value == num_parts:
            event.set()
            break

def main():
    if task_type == 'chars':
        requirements(file, alphabet, length, int(type_chars[2]))
        st = time.time()

        for length_case in range(length[0], length[1]+1):
            print(f'{BOLD}{LIGHT_GRAY}[+] TESTING PASSWORD WITH LENGTH: {length_case}{RESET}\n')

            event = Event()
            lock = Lock()
            result_queue = Queue()
            manager = Manager()
            processes = []
            shared_tasks = manager.list([""]*num_parts) # Used for displaying the process in terminal through `print_tasks()`
            shared_total = manager.Value('i', 0)
            shared_case = manager.Value('c', 0)
            limit_start_letter = []
            total_cases = (len(alphabet))**length_case

            for i in range(0, num_parts):
                limit_start_letter.append(part_size*i)

            if word_include != None:
                
                if len(''.join(word_include)) <= length_case:
                    remains = length_case - len(''.join(word_include)) # Remained positions for characters in alphabet
                    raw_lst = [','.join(word_include)] + [','.join(list(alphabet))]*remains # It is supposed to assist more than one word but currently it only works with one.
                    full_lst = list(set(itertools.permutations(raw_lst))) # Remove duplicated cases
                    total_cases = 0

                    for i in full_lst:
                        each = 1
                        for j in i:
                            each *= len(j.split(','))
                        total_cases += each

                    if len(full_lst) < num_parts:
                        print(f'{YELLOW}[+] Warning: Cannot generate {num_parts} processes. Trying {len(full_lst)} processes...{RESET}\n')
                        part_size_include = 1
                        # shared_tasks = manager.list([""]*len(full_lst))
                    else:
                        part_size_include = len(full_lst) // num_parts
                    

                    for i in range(0, num_parts):
                        if i == num_parts-1:
                            task_args = full_lst[i : len(full_lst)]
                        else:
                            task_args = full_lst[i : part_size_include+i]

                        p = Process(target=chars_task, args=(i, file, task_args, event, result_queue, shared_tasks, shared_total, shared_case, lock))
                        processes.append(p)
                        
                else:
                    print(f'{RED}Error: Length of included word(s) is greater than given length{RESET}')
                    raise SystemExit

            else:
                for i in range(0, num_parts):
                    task_args = [list(alphabet)]*(length_case-1)
                    start_letter = [alphabet[part_size*i]]
                    limit = limit_start_letter[i+1] if i != num_parts-1 else len(alphabet) # Limit the current `start_letter` to the `start_letter` of the next task so that it won't run until the end of the alphabet

                    for next_letter in range(part_size*i+1, limit):
                        start_letter.append(alphabet[next_letter]) # Add all other letters after `start_letter` in the alphabet to run all the cases

                    task_args = [start_letter] + task_args # Add `start_letter` list to the `task_args` list
                
                    p = Process(target=chars_task, args=(i, file, task_args, event, result_queue, shared_tasks, shared_total, shared_case, lock))
                    processes.append(p)

            print_tasks_proc = Process(target=print_tasks, args=(shared_tasks, shared_case, total_cases, st))
            processes.append(print_tasks_proc)

            check_finish_proc = Process(target=check_finish, args=(shared_total, num_parts, event))
            processes.append(check_finish_proc)

            for p in processes:
                p.start()
                
            event.wait() # Wait for processes end to continue the code below

            for p in processes:
                if p.is_alive():
                    p.terminate()

            et = time.time()
            if not result_queue.empty():
                delta = et-st
                print(f"{LIGHT_GREEN}[+] CORRECT PASSWORD: {result_queue.get()}{RESET}")
                print('[+] Time usage : {:02.0f}:{:02.0f}:{:02.0f}:{:06.3f}'.format(delta//86400, (delta%86400)//3600, ((delta%86400)%3600)//60, round(((delta%86400)%3600)%60, 3)))
                print('-'*50 + '\n\n')
                break
            else:
                print(f"{YELLOW}[+] Password not found with length: {length_case}{RESET}")
                print('-'*50 +'\n\n')

                if log == None:
                    time.sleep(0.5)
                    print((UP + CLEAR)*20, end="")
                
    elif task_type == 'list':
        requirements(file, alphabet, length, 0)

        st = time.time()
        event = Event()
        result_queue = Queue()
        lock = Lock()
        manager = Manager()
        processes = []
        shared_tasks = manager.list([""]*num_parts)
        shared_total = manager.Value('i', 0)
        shared_case = manager.Value('c', 0)
        total_cases = len(lines)

        for i in range(0, num_parts):
            if i == num_parts-1:
                list_range = [i*part_size, len(lines)] # The rest of the list
            else:
                list_range = [i*part_size, i*part_size + part_size]
            
            p = Process(target=list_task, args=(i, file, list_range, event, result_queue, shared_tasks, shared_total, shared_case, lock))
            processes.append(p)

        print_tasks_proc = Process(target=print_tasks, args=(shared_tasks, shared_case, total_cases))
        processes.append(print_tasks_proc)

        check_finish_proc = Process(target=check_finish, args=(shared_total, num_parts, event))
        processes.append(check_finish_proc)

        for p in processes:
            p.start()
        event.wait()
        for p in processes:
            if p.is_alive():
                p.terminate()

        et = time.time()
        if not result_queue.empty():
            print(f"{LIGHT_GREEN}[+] CORRECT PASSWORD: {result_queue.get()}{RESET}")
        else:
            print(f"{YELLOW}[+] Password not found with given list!{YELLOW}")
  
if __name__ == "__main__":

    detail(help_detail)

    main()
