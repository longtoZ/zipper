# !/usr/bin/env python3
# coding:utf-8

import os
import time
from multiprocessing import Event, Queue, Process, Manager, Lock
from zipfile import ZipFile
from unrar import rarfile
import itertools
import string
import argparse



# ANSI ESCAPE SEQUENCES COLOR

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


def detail(help_detail):
    if help_detail == 'chars':
        print(
f"""
FORMAT: --chars {LIGHT_BLUE}[ALPHABET]{RESET} {LIGHT_GREEN}[LENGTH]{RESET} {LIGHT_CYAN}[PROCESS]{RESET}

+ {LIGHT_BLUE}[ALPHABET]{RESET} : Default type: all, letters, lowercase, uppercase, digits, punctuation. Or you can pass your custom alphabet instead of using default one (ex: 12345abcd, XYZ!@#$)
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

    if file != None and os.path.exists(file) == False:
        check = False
        error.append(f"FileNotFoundError: No such file or directory: '{file}'")

    if int(process) > 10:
        check = False
        error.append('ProcessLimitError: Maximum of process is 10')

    if type_chars != None and type_lst != None:
        check = False
        error.append('OptionError: Choose "--chars" or "--list" only, not both!')
    
    if check == False:
        for i in error:
            print(f'{RED}{i}{RESET}')
        raise SystemExit
    
def alphabet_format(alphabet):
    if alphabet == 'all':
        return string.printable.strip()
    elif alphabet == 'letters':
        return string.ascii_letters
    elif alphabet == 'lowercase':
        return string.ascii_lowercase
    elif alphabet == 'uppercase':
        return string.ascii_uppercase
    elif alphabet == 'digits':
        return string.digits
    elif alphabet == 'punctuation':
        return string.punctuation
    else:
        return alphabet

def extract_format(t_file, pwd):
    try:
        if '.zip' in t_file:
            zip = ZipFile(t_file, 'r')
            zip.extractall(
                path=t_file.replace('.zip','')+"_uncompressed", 
                pwd=pwd.encode('utf-8')
            )
        elif '.rar' in t_file:
            rar = rarfile.RarFile(t_file, pwd=pwd)
            rar.extractall(
                path=t_file.replace('.rar','')+"_uncompressed"
            )
    except TypeError:
        print(f"FileNotFoundError: No such file or directory: '{file}'")
        raise SystemExit


parser = argparse.ArgumentParser(description="Python password bruteforce program using multiprocessing. Copyright © 2023 NautilusZ")
parser.add_argument('--detail', metavar='TYPE', type=str, help="Detailed instruction of 'chars' or 'list' option")
parser.add_argument('--file', type=str, help="Supported extension: .rar, .zip")
parser.add_argument('--chars', metavar='', nargs='+', type=str, help="Character-based brute-force. use '--detail chars' for instruction")
parser.add_argument('--list', metavar='', nargs='+', type=str, help="List-based brute-force. use '--detail list' for instruction")
task_args = vars(parser.parse_args())

help_detail = task_args['detail']
file = task_args['file']
type_chars = task_args['chars']
type_lst = task_args['list']

alphabet = ''
length = []
num_parts = 0
part_size = 0
task_type = ''


if type_chars != None and type_lst == None:
    if len(type_chars) != 3:
        print(f'{RED}ArgumentError: Expected 3 arguments{RESET}')
        raise SystemExit
    else:
        task_type = 'chars'
        alphabet = alphabet_format(type_chars[0])
        length = [int(i) for i in type_chars[1].split(',')]
        num_parts = int(type_chars[2]) if int(type_chars[2]) < len(alphabet) else len(alphabet)
        part_size = len(alphabet) // num_parts

elif type_lst != None and type_chars == None:
    if len(type_lst) != 2:
        print(f'{RED}ArgumentError: Expected 2 arguments{RESET}')
        raise SystemExit
    else:
        task_type = 'list'
        if type_lst[0].endswith('.txt'):
            txt = open(type_lst[0], 'r', encoding='ISO-8859-1')
            lines = txt.readlines()

            num_parts = int(type_lst[1]) if int(type_lst[1]) < len(lines) else len(lines)
            part_size = len(lines) // num_parts
        else:
            print(f'{RED}FileTypeError: Must be a .txt file{RESET}')
            raise SystemExit
        
if (type_chars != None or type_lst != None) and file == None:
    print(f"{RED}FileNotFoundError: No such file or directory: '{file}'{RESET}")
    raise SystemExit
    
    
def chars_task(n, file, task_args, event, result_queue, shared_tasks):
    # print("task_args:" + str(task_args))
    for i in itertools.product(*task_args):
        pwd = ''.join(i)
        shared_tasks[n] = f"TESTING: {pwd} in [{CYAN}task {n}{RESET}]"
        try:
            extract_format(file, pwd)
            result_queue.put(f"{LIGHT_GREEN}{pwd}{RESET}")
            event.set()
            break
        except RuntimeError:
            continue
    return

def list_task(n, file, list_range, event, result_queue, shared_tasks, lock):
    rar = None  # Initialize rarfile.RarFile outside the loop
    for i in range(list_range[0], list_range[1]):
        lock.acquire()
        pwd = lines[i].replace('\n', '')
        if rar is None:
            # Acquire the lock before creating the rarfile.RarFile instance
            shared_tasks[n] = f"TESTING: {pwd} in [{CYAN}task {n}{RESET}]"
            try:
                extract_format(file, pwd)
                result_queue.put(f"{LIGHT_GREEN}{pwd}{RESET}")
                event.set()
                break  # Password found, terminate the loop
            except RuntimeError:
                continue
            finally:
                lock.release()

    if rar is not None:
        rar.close()
    
    return

def print_tasks(shared_tasks):
    while True:
        print('\n'.join(shared_tasks))
        print((UP + CLEAR)*num_parts, end="")


if __name__ == "__main__":

    detail(help_detail)

    if task_type == 'chars':
        requirements(file, alphabet, length, int(type_chars[2]))
        for length_case in range(length[0], length[1]+1):

            st = time.time()
            event = Event()
            result_queue = Queue()
            manager = Manager()
            processes = []
            shared_tasks = manager.list([""]*num_parts) # Used for displaying the process in terminal through `print_tasks()`

            for i in range(0, num_parts):
                task_args = [list(alphabet)]*(length_case-1)
                start_letter = [alphabet[part_size*i]]

                for next_letter in range(part_size*i+1, len(alphabet)):
                    start_letter.append(alphabet[next_letter]) # Add all other letters after `start_letter` in the alphabet to run all the cases

                task_args = [start_letter] + task_args # Add `start_letter` list to the `task_args` list
                
                p = Process(target=chars_task, args=(i, file, task_args, event, result_queue, shared_tasks))
                processes.append(p)

            print_tasks_proc = Process(target=print_tasks, args=(shared_tasks,))
            processes.append(print_tasks_proc)

            for p in processes:
                p.start()
            event.wait()
            for p in processes:
                if p.is_alive():
                    p.terminate()

            et = time.time()
            if not result_queue.empty():
                print(f"CORRECT PASSWORD: {result_queue.get()}")
                print(f"Finished in {et-st}s")
                break
            else:
                print(f"Password not found with length: {length_case}")
                print(f"Finished in {et-st}s\n")
                
    elif task_type == 'list':
        requirements(file, alphabet, length, 0)

        st = time.time()
        event = Event()
        result_queue = Queue()
        lock = Lock()
        manager = Manager()
        processes = []
        shared_tasks = manager.list([""]*num_parts)
        

        for i in range(0, num_parts):
            if i == num_parts-1:
                list_range = [i*part_size, len(lines)] # The rest of the list
            else:
                list_range = [i*part_size, i*part_size + part_size]
            
            p = Process(target=list_task, args=(i, file, list_range, event, result_queue, shared_tasks, lock))
            processes.append(p)

        print_tasks_proc = Process(target=print_tasks, args=(shared_tasks,))
        processes.append(print_tasks_proc)

        for p in processes:
            p.start()
        event.wait()
        for p in processes:
            if p.is_alive():
                p.terminate()

        et = time.time()
        if not result_queue.empty():
            print(f"CORRECT PASSWORD: {result_queue.get()}")
            print(f"Finished in {et-st}s")
        else:
            print(f"Password not found with given list!")
            print(f"Finished in {et-st}s\n")     