# Keep Mega Accounts Active
# mega deletes inactive accounts
# reads credentials from a file called accounts.csv
# run this once a month to be safe (you'll forget so setup a systemd timer or cron)

import csv
import subprocess
import time


def main():
    with open("accounts.csv") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if not row or row[0] == "Email":
                continue

            # CSV Format
            # ["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"]
            time.sleep(1)

            email = row[0].strip()
            password = row[1].strip()

            # login
            login = subprocess.run(
                [
                    "megatools",
                    "ls",
                    "-u",
                    email,
                    "-p",
                    password,
                ],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if "/Root" in login.stdout:
                print(f"\r> [{email}]: Successefully logged in", end="\033[K", flush=True)
            else:
                print(f"\r> [{email}]: ERROR", end="\033[K\n", flush=True)


if __name__ == "__main__":
    main()
