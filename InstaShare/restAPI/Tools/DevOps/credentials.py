import csv
import os

def get_credentials():
    path = "../credentials.csv"
    if os.path.exists(path):
        with open(path) as csvfile:
            cred_file = csv.reader(csvfile)
            data = [row for row in cred_file]
            creds = {
                'access': str(data[1][0]).replace(' ', ''),
                'secret': str(data[1][1]).replace(' ', ''),
                'bucket': 'instashare-images'
            }
            return creds
    else:
        print('Path doesnt exist')
