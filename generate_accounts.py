# Create New Mega Accounts
# saves credentials to a file called accounts.csv

import requests
import subprocess
import os
import time
import re
import random
import string
import csv
import threading
import argparse
import pymailtm
from pymailtm.pymailtm import CouldNotGetAccountException, CouldNotGetMessagesException
from faker import Faker
fake = Faker()

# Custom function for checking if the argument is below a certain value
def check_limit(value):
    ivalue = int(value)
    if ivalue <= 8:
        return ivalue
    else:
        raise argparse.ArgumentTypeError(f"You cannot use more than 8 threads.")

# set up command line arguments
parser = argparse.ArgumentParser(description="Create New Mega Accounts")
parser.add_argument(
    "-n",
    "--number",
    type=int,
    default=3,
    help="Number of accounts to create",
)
parser.add_argument(
    "-t",
    "--threads",
    type=check_limit,
    default=None,
    help="Number of threads to use for concurrent account creation",
)
parser.add_argument(
    "-p",
    "--password",
    type=str,
    default=None,
    help="Password to use for all accounts",
)
args = parser.parse_args()


def find_url(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]

def get_random_string(length):
    """Generate a random string with a given length."""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join(random.choice(letters) for _ in range(length))


class MegaAccount:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def generate_mail(self):
        """Generate mail.tm account and return account credentials."""
        for i in range(5):
            try:
                mail = pymailtm.MailTm()
                acc = mail.get_account()
            except CouldNotGetAccountException:
                print(f"\r> Could not get new Mail.tm account. Retrying ({i+1} of 5)...", end="\n")
                sleep_output = ""
                for i in range(random.randint(8, 15)):
                    sleep_output += ". "
                    print("\r"+sleep_output, end="\033[K", flush=True)
                    time.sleep(1)
            else:
                break
        else:
            print("\nCould not get account. You are most likely blocked from Mail.tm.")
            print("Please wait 5 minutes and try again with a lower number of accounts/threads.")
            exit()

        self.email = acc.address
        self.email_id = acc.id_
        self.email_password = acc.password

    def get_mail(self):
        """Get the latest email from the mail.tm account"""
        while True:
            try:
                mail = pymailtm.Account(self.email_id, self.email, self.email_password)
                messages = mail.get_messages()
                break
            except (CouldNotGetAccountException, CouldNotGetMessagesException):
                print("> Could not get latest email. Retrying...")
                time.sleep(random.randint(5, 15))
        if len(messages) == 0:
            return None
        return messages[0]

    def register(self):
        # Generate mail.tm account and return account credentials.
        self.generate_mail()

        print(f"\r> [{self.email}]: Registering account...", end="\033[K", flush=True)

        # begin resgistration
        registration = subprocess.run(
            [
                "megatools",
                "reg",
                "--scripted",
                "--register",
                "--email",
                self.email,
                "--name",
                self.name,
                "--password",
                self.password,
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.verify_command = registration.stdout

        return self.email

    def verify(self):
        # check if there is mail
        confirm_message = None
        for i in range(5):
            confirm_message = self.get_mail()
            if confirm_message is not None and "verification required".lower() in confirm_message.subject.lower():
                confirm_message = self.get_mail()
                break
            print(f"\r> [{self.email}]: Waiting for verification email... ({i+1} of 5)", end="\033[K", flush=True)
            time.sleep(5)

        # get verification link
        if confirm_message is None:
            print(f"\r> [{self.email}]: Failed to verify account. There was no verification email. Please open an issue on github.", end="\033[K", flush=True)
            exit()

        links = find_url(confirm_message.text)

        self.verify_command = str(self.verify_command).replace("@LINK@", links[0])

        # perform verification
        verification = subprocess.run(
            self.verify_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        if "registered successfully!" in str(verification.stdout):
            print(f"\r> [{self.email}] Successefully registered and verified.", end="\033[K", flush=True)
            print(f"\n{self.email} - {self.password}")

            # save to file
            with open("accounts.csv", "a", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                # last column is for purpose (to be edited manually if required)
                csvwriter.writerow([self.email, self.password, "-", self.email_password, self.email_id, "-"])
        else:
            print("Failed to verify account. Please open an issue on github.")


def new_account():
    if args.password is None:
        password = get_random_string(random.randint(8, 14))
    else:
        password = args.password
    acc = MegaAccount(fake.name(), password)
    email = acc.register()
    print(f"\r> [{email}]: Registered. Waiting for verification email...", end="\033[K", flush=True)
    acc.verify()


if __name__ == "__main__":
    # Check if CSV file exists, and if not create it and add header
    if not os.path.exists("accounts.csv"):
        with open("accounts.csv", "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"])

    # Check if CSV file is using the correct format
    with open("accounts.csv") as csvfile:
        csvreader = csv.reader(csvfile)
        if next(csvreader) != ["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"]:
            print("CSV file is not in the correct format. Please use the convert_csv.py script to convert it.")
            exit()
    
    # Parse arguments and generate accounts accordingly
    if args.threads:
        print(f"Generating {args.number} accounts using {args.threads} threads.")
        threads = []
        for i in range(args.number):
            t = threading.Thread(target=new_account)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    else:
        print(f"Generating {args.number} accounts.")
        for _ in range(args.number):
            new_account()

