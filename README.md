<h1 align="center">
  <img src="./img/readme-icon.png" alt="Discord OAuth" width="512">
  <br>
  MEGA.nz Account Creator
</h1>

<h4 align="center">An Open Source demonstration of creating / managing multiple  <a href="https://mega.nz" target="_blank">MEGA.nz</a> accounts.</h4>

<br>

<p align="center">
  <!--License-->
  <a href="https://github.com/f-o/MEGA-Account-Generator/blob/master/LICENSE">
      <img src="https://img.shields.io/github/license/f-o/MEGA-Account-Generator">
  </a>
  <!--Contributions-->
  <a href="https://github.com/f-o/MEGA-Account-Generator/graphs/contributors" alt="Contributors">
      <img src="https://img.shields.io/github/contributors/f-o/MEGA-Account-Generator" />
  </a>
  <!--Stars-->
  <a href="https://github.com/f-o/MEGA-Account-Generator/stargazers">
      <img src="https://img.shields.io/github/stars/f-o/MEGA-Account-Generator">
  </a>
  <!--Donate-->
  <a href="#support">
    <img src="https://img.shields.io/badge/$-donate-ff69b4.svg?maxAge=2592000&amp;style=flat">
  </a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#acknowledgements">Acknowledgements</a> •
  <a href="#support">Support</a> •
  <a href="#license">License</a>
</p>
<div align="center">
  <img src="./img/demo.png" alt="Discord OAuth Demo" width="800px" style="border-radius:7px;">
</div>

<br>

## Key Features

* Generate new MEGA.nz accounts in bulk
* Automatically verify emails
* Fetch information about available storage
* Keep accounts alive by logging in periodically

<br>

## How To Use

**Prerequisites:**
* [megatools](https://megatools.megous.com/) installed and added to your PATH
* Python 3.6+

**Installation:**
```bash
# Clone this repository
$ git clone https://github.com/f-o/MEGA-Account-Generator.git
# Go into the repository
$ cd MEGA-Account-Generator
# Install dependencies
$ pip install -r requirements.txt
```

**Usage:**
```bash
# Create new accounts
$ python generate_accounts.py
# Sign in to accounts to keep them alive
$ python signin_accounts.py
```

<details><summary>Click here for Advanced Usage</summary>

```bash
# Create new accounts with arguments
$ python generate_accounts.py [-h] [-n NUMBER_OF_ACCOUNTS] [-t NUMBER_OF_THREADS] [-p PASSWORD]
# Sign in to accounts to keep them alive
$ python signin_accounts.py
# Convert old CSV file to new format
$ python convert_csv.py [-h] [-i INPUT_FILE]
```

- `-n` Number of new accounts to generate. If not specified, 3 accounts will be generated.
- `-t` Number of threads to use for concurrent account creation. Maximum of 8.
- `-p` Password to use for all accounts. If not specified, a random password will be generated for each account.
- `-h` Show help.

</details>

<br>

## Convert old CSV file to new format

**What's this?**

As of May 2024, the script has updated to use a new format for the CSV file. This means that the CSV file (`accounts.csv`) will be easier to use in the future.<br>
Unfortunately the old format is not supported any more, so you will need to convert it to the new format.<br>
You will need to convert the old CSV file **only if you have accounts in the ``accounts.csv`` file from before May 2024**.


**Usage:**

```bash
# Convert old CSV file to new format
$ python convert_csv.py [-h] [-i INPUT_FILE]
```

- `-i` Path to the input CSV file. If not specified, `accounts.csv` will be used.
- `-h` Show help.

<br>

## FAQ

- Will this automatically verify emails?
  - Yes, the script will automatically fetch the verification link from the email, and use it to verify the account.

- Can I log in to the accounts, on the web, after generating them?
  - Yes, that is how this script is intended to be used. Simply copy the email address and password from the CSV file and log in to the account.

- There are multiple passwords in the CSV file. Which one should I use?
  - As of May 2024, all columns have appropriate headers.
  - You will need to use the password in the second columns titled `MEGA Password`.

- What's with the other password then? And why do I need the `Mail.tm ID`?
  - The other password, in the `Mail.tm Password` column, is the password for the Mail.tm account.
  - You can use this password to sign in to the temporary Mail.tm account on their website.
  - In order to access the Mail.tm account, through their API, we also need the ID of the account. This is stored in the case it will be needed in the future.

- What's with the `-p`/`--password` flag? Do I need it?
  - The `-p` flag is optional.
  - You can use this to specify a password for all accounts. If not specified, a random password will be generated for each account.

- Can I generate multiple accounts in parallel?
  - Yes, this script can generate multiple accounts in parallel using the `-t` flag.
  - This is, however, not recommended, and will likely result in rate limits from Mail.tm.
  - The script will automatically retry in the event of a rate limit up to 5 times.

- Why can I only run 8 threads?
  - Because of rate limits from Mail.tm.
  - We do not want to overload their service, which they generously offer for free.

- Something is broken? I'm having trouble using this script.
  - Please [open an issue on GitHub](https://github.com/f-o/MEGA-Account-Generator/issues). Be sure to include information and screenshots.


<br>

## Acknowledgements

This software was based heavily on [IceWreck/MegaScripts](https://github.com/IceWreck/MegaScripts).<br>
His original Python script utilized [GuerillaMail](https://www.guerrillamail.com/GuerrillaMailAPI.html) to generate temporary email addresses.<br>
I've modified the script to use [Mail.tm](https://api.mail.tm/) instead, with a lot of help from [qtchaos/py_mega_account_generator](https://github.com/qtchaos/py_mega_account_generator).<br>
I highly recommend checking out both of their projects.


## Support
This project is free and open source.<br>
If you find it useful, please consider supporting the project by donating.
<br><br>
<a href="https://www.buymeacoffee.com/foxdk" target="_blank"><img src="./img/bmc-button.png" alt="Buy Me A Coffee" width="160"></a>

<br>

## License

[MIT License](https://mit-license.org/)
```
Copyright (c) 2023 Fox

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> [@f-o](https://github.com/f-o) &nbsp;&middot;&nbsp;
> [soon.to](https://soon.to)