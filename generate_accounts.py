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
import json
import asyncio
from faker import Faker
from aiohttp import ClientSession
fake = Faker()

# Custom mail.tm implementation
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Dict, List, Optional

# Mail.tm API implementation
class MailTMInvalidResponse(Exception):
    """Raised if the Mail.tm API returns an invalid response."""
    pass

def random_string(length=10):
    """Generate a random string with given length."""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

async def validate_response(response):
    """Validate the response from the Mail.tm API."""
    return response.status in [200, 201, 204]

class Token:
    """Token class for Mail.tm API."""
    def __init__(self, id, token):
        self.id = id
        self.token = token

class Account:
    """Account class for Mail.tm API."""
    def __init__(self, id, address, quota, used, isDisabled, isDeleted, createdAt, updatedAt, token, original_password):
        self.id = id
        self.address = address
        self.quota = quota
        self.used = used
        self.isDisabled = isDisabled
        self.isDeleted = isDeleted
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.token = token
        self.original_password = original_password  # Store the actual password

@dataclass
class Message:
    """Simple data class that holds a message information."""
    id_: str
    from_: Dict
    to: Dict
    subject: str
    intro: str
    text: str
    html: List[str]
    seen: bool
    data: Dict

    def open_web(self):
        """Open a temporary html file with the mail inside in the browser."""
        with NamedTemporaryFile(mode="w", delete=False, suffix=".html") as f:
            html = self.html[0].replace("\n", "<br>").replace("\r", "")
            message = """<html>
            <head></head>
            <body>
            <b>from:</b> {}<br>
            <b>to:</b> {}<br>
            <b>subject:</b> {}<br><br>
            {}</body>
            </html>""".format(self.from_, self.to, self.subject, html)
            f.write(message)
            f.flush()
            file_name = f.name
            open_webbrowser("file://{}".format(file_name))
            # Wait a second before deleting the tempfile, so that the
            # browser can load it safely
            sleep(1)
            #  os.remove(file_name)

def open_webbrowser(link: str) -> None:
    """Open a url in the browser ignoring error messages."""
    saverr = os.dup(2)
    os.close(2)
    os.open(os.devnull, os.O_RDWR)
    try:
        webbrowser.open(link)
    finally:
        os.dup2(saverr, 2)

class AsyncMailTM:
    """Async implementation of the Mail.tm API."""
    API_URL = "https://api.mail.tm"
    SSL = False

    def __init__(self, session: ClientSession = None):
        self.session = session or ClientSession()

    async def get_account_token(self, address: str, password: str) -> Token:
        """Get account token from Mail.tm API."""
        headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json"
        }
        response = await self.session.post(f"{self.API_URL}/token", data=json.dumps({
            "address": address,
            "password": password
        }), headers=headers, ssl=self.SSL)
        
        if await validate_response(response):
            data = await response.json()
            return Token(data['id'], data['token'])
        
        raise MailTMInvalidResponse(f"Error response for {self.API_URL}/token", await response.json())

    async def get_domains(self):
        """Get domains from Mail.tm API."""
        response = await self.session.get(f"{self.API_URL}/domains", ssl=self.SSL)
        
        if await validate_response(response):
            data = await response.json()
            return data['hydra:member']
        
        raise MailTMInvalidResponse(f"Error response for {self.API_URL}/domains", await response.json())

    async def get_account(self, address: str = None, password: str = None):
        """Create and get account from Mail.tm API."""
        if address is None:
            domains = await self.get_domains()
            domain = domains[0]['domain']
            address = f"{random_string()}@{domain}"
    
        if password is None:
            password = random_string(8)  # Generate a readable password
    
        payload = {
            "address": address,
            "password": password
        }
    
        response = await self.session.post(f"{self.API_URL}/accounts", json=payload, ssl=self.SSL)
    
        if await validate_response(response):
            data = await response.json()
            token = await self.get_account_token(address=address, password=password)
            return Account(
                id=data['id'],
                address=data['address'],
                quota=data['quota'],
                used=data['used'],
                isDisabled=data['isDisabled'],
                isDeleted=data['isDeleted'],
                createdAt=data['createdAt'],
                updatedAt=data['updatedAt'],
                token=token,
                original_password=password  # Save the original password
            )
    
        raise MailTMInvalidResponse(f"Error response for {self.API_URL}/accounts", await response.json())


    async def get_messages(self, token: str, page: int = 1):
        """Get messages from Mail.tm API."""
        response = await self.session.get(f"{self.API_URL}/messages?page={page}",
                                      headers={'Authorization': f'Bearer {token}'},
                                      ssl=self.SSL)
        
        if await validate_response(response):
            data = await response.json()
            messages = []
            for msg_data in data['hydra:member']:
                # Get full message details
                full_msg = await self.get_message_by_id(msg_data['id'], token)
                messages.append(Message(
                    id_=msg_data['id'],
                    from_=msg_data['from'],
                    to=msg_data['to'],
                    subject=msg_data['subject'],
                    intro=msg_data['intro'],
                    text=full_msg['text'],
                    html=[full_msg['html']] if isinstance(full_msg['html'], str) else full_msg['html'],
                    seen=msg_data['seen'],
                    data=msg_data
                ))
            return messages
        
        raise MailTMInvalidResponse(f"Error response for {self.API_URL}/messages", await response.json())

    async def get_message_by_id(self, message_id: str, token: str):
        """Get message by ID from Mail.tm API."""
        response = await self.session.get(f"{self.API_URL}/messages/{message_id}",
                                      headers={'Authorization': f'Bearer {token}'},
                                      ssl=self.SSL)
        
        if await validate_response(response):
            return await response.json()
        
        raise MailTMInvalidResponse(f"Error response for {self.API_URL}/messages/{message_id}", await response.json())

# Synchronous wrapper for the async API
class SyncMailTM:
    """Synchronous wrapper for the async Mail.tm API."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = None
    
    def _ensure_client(self):
        """Ensure that the client is initialized."""
        if self.client is None:
            # Create session inside the loop's running context
            session = self.loop.run_until_complete(self._create_session())
            self.client = AsyncMailTM(session)
    
    async def _create_session(self):
        """Create aiohttp ClientSession inside an async context."""
        return ClientSession()
    
    def get_account(self):
        """Get account from Mail.tm API."""
        self._ensure_client()
        account = self.loop.run_until_complete(self.client.get_account())
        return SyncAccount(account, self)
    
    def close(self):
        """Close the client session."""
        if self.client and self.client.session:
            self.loop.run_until_complete(self.client.session.close())
            self.loop.close()



class Account:
    """Account class for Mail.tm API."""
    def __init__(self, id, address, quota, used, isDisabled, isDeleted, createdAt, updatedAt, token, original_password):
        self.id = id
        self.address = address
        self.quota = quota
        self.used = used
        self.isDisabled = isDisabled
        self.isDeleted = isDeleted
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.token = token
        self.original_password = original_password  # Store the actual password

# In the AsyncMailTM class:
async def get_account(self, address: str = None, password: str = None):
    """Create and get account from Mail.tm API."""
    if address is None:
        domains = await self.get_domains()
        domain = domains[0]['domain']
        address = f"{random_string()}@{domain}"
    
    if password is None:
        password = random_string(8)  # Generate a readable password
    
    payload = {
        "address": address,
        "password": password
    }
    
    response = await self.session.post(f"{self.API_URL}/accounts", json=payload, ssl=self.SSL)
    
    if await validate_response(response):
        data = await response.json()
        token = await self.get_account_token(address=address, password=password)
        return Account(
            id=data['id'],
            address=data['address'],
            quota=data['quota'],
            used=data['used'],
            isDisabled=data['isDisabled'],
            isDeleted=data['isDeleted'],
            createdAt=data['createdAt'],
            updatedAt=data['updatedAt'],
            token=token,
            original_password=password  # Save the original password
        )
    
    raise MailTMInvalidResponse(f"Error response for {self.API_URL}/accounts", await response.json())

# In SyncAccount:
class SyncAccount:
    """Synchronous wrapper for the async Account class."""
    def __init__(self, account, mail_tm):
        self.id_ = account.id
        self.address = account.address
        self.password = account.original_password  # Use the actual password
        self.token = account.token.token
        self.mail_tm = mail_tm

    def get_messages(self):
        """Get messages from Mail.tm API."""
        messages = self.mail_tm.loop.run_until_complete(
            self.mail_tm.client.get_messages(self.token)
        )
        return messages

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
    default=1,
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
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»""'']))"
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
        self.mail_tm = SyncMailTM()
   
    def cleanup(self):
        """Clean up resources used by the MegaAccount."""
        if hasattr(self, 'mail_tm'):
            self.mail_tm.close()

    def generate_mail(self):
        """Generate mail.tm account and return account credentials."""
        for i in range(5):
            try:
                # Add delay before retrying
                if i > 0:
                    # Base delay with exponential backoff and jitter
                    base_delay = 30 * (2 ** (i - 1))
                    jitter = random.uniform(0, 15)
                    delay = base_delay + jitter
                    print(f"\r> Rate limited by Mail.tm. Waiting {delay:.1f} seconds before retry {i+1}...", end="\033[K", flush=True)
                    time.sleep(delay)
            
                self.mail_account = self.mail_tm.get_account()
                self.email = self.mail_account.address
                self.email_password = self.mail_account.password
                self.email_id = self.mail_account.id_
            
                # Add successful delay after account creation to avoid rate limits on subsequent accounts
                if i > 0:
                    print(f"\r> Account created after {i+1} attempts. Adding cooldown period of 10s...", end="\033[K", flush=True)
                    time.sleep(10)
                break
            except Exception as e:
                error_str = str(e)
                print(f"\r> Could not get new Mail.tm account. Retrying ({i+1} of 5)...", end="\n")
                print(f"Error details: {error_str}")
            
                # Add extra delay for specific rate limit errors
                if "429" in error_str:
                    extra_delay = 30 + random.randint(0, 30)
                    print(f"Rate limit detected. Adding {extra_delay} seconds of delay...")
                    time.sleep(extra_delay)


    def get_mail(self):
        """Get the latest email from the mail.tm account"""
        while True:
            try:
                messages = self.mail_account.get_messages()
                break
            except Exception:
                print("> Could not get latest email. Retrying...")
                time.sleep(random.randint(5, 15))
        if len(messages) == 0:
            return None
        return messages[0]

    def register(self):
        # Generate mail.tm account and return account credentials.
        self.generate_mail()

        print(f"\r> [{self.email}]: Registering account...", end="\033[K", flush=True)

        # begin registration
        megatools_path = r"C:\megatools-1.11.4.20250411-win64\megatools.exe"
        registration = subprocess.run(
            [
                megatools_path,
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
                break
            print(f"\r> [{self.email}]: Waiting for verification email... ({i+1} of 5)", end="\033[K", flush=True)
            time.sleep(5)

        # get verification link
        if confirm_message is None:
            print(f"\r> [{self.email}]: Failed to verify account. There was no verification email. Please open an issue on github.", end="\033[K", flush=True)
            exit()

        links = find_url(confirm_message.text)

        # Replace the 'megatools' command with the full path
        megatools_path = r"C:\megatools-1.11.4.20250411-win64\megatools.exe"
        self.verify_command = str(self.verify_command).replace("megatools", megatools_path)
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
            print(f"\r> [{self.email}] Successfully registered and verified.", end="\033[K", flush=True)
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
    try:
        email = acc.register()
        print(f"\r> [{email}]: Registered. Waiting for verification email...", end="\033[K", flush=True)
        acc.verify()
    finally:
        # Always clean up resources even if an error occurs
        acc.cleanup()


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
            # Limit the number of concurrent threads
            if len(threads) >= args.threads:
                for t in threads:
                    t.join()
                threads = []
        # Wait for any remaining threads
        for t in threads:
            t.join()
    else:
        print(f"Generating {args.number} accounts.")
        for _ in range(args.number):
            new_account()