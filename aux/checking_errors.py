import os

os.chdir('/')

try:
    print('Errors:')
    error_file = 'error.log'
    with open(error_file, 'r') as file:
        print(file.read())
        
    print('SD Errors:')
    with open('/sd/error.log', 'r') as file:
        print(file.read())
except Exception as e:
    print('unable to open error')
    print(e)