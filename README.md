# Zipper - Multiprocessing Password Brute-Force

This Python script allows you to perform password brute-forcing using multiprocessing. It supports two modes of operation: character-based brute-forcing and list-based brute-forcing. The script utilizes multiple processes to speed up the password cracking process.

## Prerequisites

- Python 3.x
- Required Python packages: `unrar`, `zipfile`, `argparse`

You can install the required packages using pip:

```
pip install unrar
```

<details>
<summary><i>How to set path to <code>unrar</code> library in Python?</i></summary>
<br>
These steps will help you to setup for <b>Windows</b> environment.

1. Download the file via the [link](https://www.rarlab.com/rar/UnRARDLL.exe) and install it.
2. For easy replication the following steps, choose the default path, C:\Program Files (x86)\UnrarDLL\
3. Go to <b>Environment Variables</b> window and selected <b>Advanced</b>.
4. Click <b>Environment Setting</b>.
5. Under the <b>User variables</b>, select New.
6. In the <b>New User Variables</b>, rename the Variable name as <b>UNRAR_LIB_PATH</b>
7. To select the <b>Variable Value</b>, select Browse file. Depending on your system, 64bit enter C:\Program Files (x86)\UnrarDLL\x64\UnRAR64.dll, if your system is 32bit enter C:\Program Files (x86)\UnrarDLL\UnRAR.dll.
8. Save the environment path and return to your code editor.
</details>

## Usage

To run the script, use the following command:

```
python zipper.py [options]
```

### Options

The script supports the following options:

- `--detail TYPE`: Provides detailed instructions for a specific option type. Valid values for TYPE are `chars` and `list`.
- `--file FILE`: Specifies the path to the compressed file (either .rar or .zip) that you want to crack.
- `--chars ALPHABET LENGTH PROCESS`: Performs character-based brute-forcing. `ALPHABET` represents the character set to use, `LENGTH` specifies the password length range (format: START_LENGTH,STOP_LENGTH), and `PROCESS` indicates the number of parallel processes to run.
- `--list TXT_FILE PROCESS`: Performs list-based brute-forcing. `TXT_FILE` (.txt only) specifies the path to a text file containing a list of passwords to test, and `PROCESS` indicates the number of parallel processes to run.

### Examples

- Character-based brute-forcing:

  ```
  python zipper.py --file test.rar --chars digits 3,8 4
  ```

  This command will attempt to crack the password using all possible characters, with password lengths ranging from 3 to 8 characters. It will use 4 parallel processes for faster cracking.

- List-based brute-forcing:

  ```
  python zipper.py --file test.zip --list passwords.txt 2
  ```

  This command will read the passwords from the `passwords.txt` file and attempt to crack the password using the provided list. It will use 2 parallel processes for faster cracking.

## Limitations

The script is being developed by a 12th grader so you may encounter problems while using it, and the code is quite like a mess as well. So feel free to give feedback to me.
<br><br>
*Thanks for trying!*