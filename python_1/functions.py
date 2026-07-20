def greet_user():
    print('------------------------')
    print('Say Hello!!!')
    print('Hope you have a nice day')
    print('------------------------')

greet_user()

#Middle
#Middle
#Middle
#Middle
#Middle

greet_user()

greet_user()





#function without parameters
def greet_user():
    print('------------------------')
    print('Say Hello!!!')
    print('Hope you have a nice day')
    print('------------------------')

#function with parameters
def greet_user(username):
    print('------------------------')
    print('Say Hello {username}!!!')
    print('Hope you have a nice day')
    print('------------------------')




#Calling a function without an argument
# greet_user()

#Calling a function with an argument
def greet_user(username):
    print('------------------------')
    print('Say Hello', username,'!!!')
    print('Hope you have a nice day')
    print('------------------------')


greet_user('Kiona')

#Calling a function with multiple arguments
def greet_user(username, location): 
    print('------------------------')
    print('Say Hello', username, location,'!!!')
    print('Hope you have a nice day')
    print('------------------------')


greet_user('Kiona','Cali')


#Count down timer froM Mostafa's Teachback 7/15/2026
import time
for i in range (10,0,-1):
    print(i)
    time.sleep(1)

print("time off")

