# Helper script to convert old csv format to new csv format
import os
import csv
import argparse

parser = argparse.ArgumentParser(description="Convert old csv format to new csv format")
parser.add_argument("-i", "--input", default="accounts.csv", type=str, help="Input file")
args = parser.parse_args()

if not os.path.exists(args.input):
    print("Input file does not exist.")
    exit()

with open(args.input) as csvfile:
    csvreader = csv.reader(csvfile)
    if next(csvreader) == ["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"]:
        print("CSV file has already been converted.")
        exit()
    else:
        print("Converting CSV file...")

# Move file to .old
os.rename(args.input, "accounts.old.csv")

with open("accounts.old.csv") as csvfile:
    csvreader_old = csv.reader(csvfile)
    # Create new file
    with open(args.input, "a", newline='') as csvfile:
        csvwriter_new = csv.writer(csvfile)
        csvwriter_new.writerow(["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"])

        for row in csvreader_old:
            if not row:
                continue  # Skip empty rows
            csvwriter_new.writerow([row[0], row[4].split(":")[1], "-", row[2], row[1], row[5]])

