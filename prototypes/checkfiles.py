import machine
import os

print(os.listdir())
print(os.getcwd())
# os.mkdir('/components')
os.chdir('../')
# print(os.listdir())
print(os.listdir())