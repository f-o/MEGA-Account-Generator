# Create New Mega Accounts
# saves credentials to a file called accounts.csv

import requests
import subprocess
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

def generate_mail():
    """Generate mail.tm account and return account credentials."""
    mail = pymailtm.MailTm()

    while True:
        try:
            acc = mail.get_account()
            break
        except CouldNotGetAccountException:
            print("> Could not get account. Retrying...")

    return acc.id_, acc.address, acc.password


class MegaAccount:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def generate_mail(self):
        """Generate mail.tm account and return account credentials."""
        while True:
            try:
                mail = pymailtm.MailTm()
                break
            except CouldNotGetAccountException:
                print("> Could not get account. Retrying...")
                time.sleep(random.randint(5, 15))

        while True:
            try:
                acc = mail.get_account()
                break
            except CouldNotGetAccountException:
                print("> Could not get account. Retrying...")

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

        print(f"Email: {self.email}")
        print(f"Email Password: {self.email_password}")
        print(f"Name: {self.name}")
        print(f"Password: {self.password}")

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

    def verify(self):
        # check if there is mail
        confirm_message = None
        for i in range(5):
            confirm_message = self.get_mail()
            if confirm_message is not None and "verification required".lower() in confirm_message.subject.lower():
                confirm_message = self.get_mail()
                break
            time.sleep(5)

        # get verification link
        if confirm_message is None:
            return

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
            print("> Successefully registered and verified with:")
            print(f"{self.email} - {self.password}")

            # save to file
            with open("accounts.csv", "a") as csvfile:
                csvwriter = csv.writer(csvfile)
                # last column is for purpose (to be edited manually if required)
                csvwriter.writerow([self.email, self.email_id, self.email_password, self.name, self.email+":"+self.password, "-"])
        else:
            print("Failed.")


def new_account():
    if args.password is None:
        password = get_random_string(random.randint(8, 14))
    else:
        password = args.password
    acc = MegaAccount(fake.name(), password)
    acc.register()
    print("> Registered. Waiting for verification email...")
    acc.verify()


if __name__ == "__main__":
    for count in range(args.number):
        t = threading.Thread(target=new_account)
        t.start()
