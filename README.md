# Zipper - Multiprocessing Password Brute-Force

This Python script allows you to perform password brute-forcing using multiprocessing. It supports two modes of operation: character-based brute-forcing and list-based brute-forcing. The script utilizes multiple processes to speed up the password cracking process.

## Prerequisites

- Python 3.x
- Required Python packages: [**zipfile**](https://docs.python.org/3/library/zipfile.html), [**argparse**](https://docs.python.org/3/library/argparse.html)


> **Warning**
>
> Do not remove **UnRAR.exe** since it is used for RAR extraction.


## Usage

To run the script, use the following command:

```
python zipper.py [options]
```

### Options

The script supports the following options:

| Command | Description |
| --- | --- |
| `--detail TYPE` | Provides detailed instructions for a specific option type. Valid values for TYPE are `chars` and `list`. |
| `--file DEPARTURE_PATH DESTINATION_PATH` | Specifies the path to the compressed file (either .rar or .zip) that you want to crack. Leave `DESTINATION_PATH` empty to extract right at working directory. | 
| `--chars ALPHABET LENGTH PROCESS` | Performs character-based brute-forcing. `ALPHABET` represents the character set to use, `LENGTH` specifies the password length range (format: START_LENGTH,STOP_LENGTH), and `PROCESS` indicates the number of parallel processes to run. |
| `--list TXT_FILE PROCESS` | Performs list-based brute-forcing. `TXT_FILE` (.txt only) specifies the path to a text file containing a list of passwords to test, and `PROCESS` indicates the number of parallel processes to run. |
| `--include WORD` | Add one word to the tested string, but make sure the length is maintained. If the length of the inserted word exceeds the given length, an error will be thrown. |
| `--log` | Log the previous tested case in terminal. |
| `--wait` | Wait for a specific time before starting next password trial *(recommended for .rar).* |

### Examples

- Character-based brute-forcing:

  ```
  python zipper.py --file test.rar --chars digits 3,8 4
  ```

  This command will attempt to crack the password using all possible characters, with password lengths ranging from 3 to 8 characters. It will use 4 parallel processes for faster cracking.

- List-based brute-forcing:

  ```
  python zipper.py --file test.zip ./path/to/extract/ --list passwords.txt 2
  ```

  This command will read the passwords from the `passwords.txt` file and attempt to crack the password using the provided list. It will use 2 parallel processes for faster cracking.

## Limitations

The script is being developed by a 12th grader so you may encounter problems while using it, and the code is quite like a mess as well. So feel free to give feedback to me.
<br><br>
*Thanks for trying!*