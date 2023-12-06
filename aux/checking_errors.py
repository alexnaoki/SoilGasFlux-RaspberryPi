import os

os.chdir('/')

try:
    error_file = 'error.log'
    with open(error_file, 'r') as file:
        print(file.read())
except:
    print('unable to open error')