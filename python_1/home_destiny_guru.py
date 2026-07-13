#Welcome message
print("Welcome to Destiny Guru! Your ultimate guide to weather mapping!")

#Hardcoding these values to represent the useer's credentials
correct_username='KW_Destiny'
correct_password='DestinyGuru123'
computer_weather=76
user_retries=1

#User input for credentials
user_name=input('Please enter your username: ')
user_password=input(('Thank You ')+correct_username+'! Please enter your password: ')

#Error handling for incorrect credentials
while user_name !=correct_username or user_password !=correct_password:
    #Stop user if one of the login credentials is incorrect
    print('The incorrect username or password has been provided. Please try again.')
    user_name=input('Please enter your username: ')
    user_password=input('Thank You. Please enter your password: ')

#Second welcome message after successful login
print("Welcome " + user_name + "! Let's Map Your Weather Destiny!")

#User retry attempt entry point
#while retry_attempt

#Weather and location input from user for weather mapping
raining=int(input("Is it raining? Press 1 for Yes or 0 for No: "))
at_home=int(input("Where are you? Press 1 for Home or 0 for Work: "))

#Weather and location data combination logic for weather mapping
#Raining and at home also raining and not at home conditions for weather mapping
# if raining and at_home:
#     print('It is raining, stay home and do something fun! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')
# elif raining and not at_home:
#     print('It is raining, and its not safe to travel home! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')

# #Not raining and at home also not raining and not at home conditions for weather mapping
# if not raining and at_home:
#     print('It is not raining, and its safe to travel to work! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')
# elif not raining and not at_home:
#     print('It is not raining, and its safe to travel home! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')

#Example of more efficient code for weather mapping using nested if statements  
if raining and at_home:
    print('It is raining, stay home and do something fun! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')
elif raining and not at_home:
    print('It is raining, and its not safe to travel home! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')
elif not raining and at_home:
    print('It is not raining, and its safe to travel to work! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')
elif not raining and not at_home:
    print('It is not raining, and its safe to travel home! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')

#Tenary operator example for weather mapping
#result= ''


#Thank and restart process message for user after weather mapping
retry_attempt=input('Thank you for using Destiny Guru! We hope you have a great day! \nWould you like to restart the process? Press y for Yes or n for No: ')

if retry_attempt.lower()=='y':
    print('Great! We will restart the process for you!')
    
while retry_attempt != 'y' and retry_attempt != 'n':
    retry_attempt=input('Invalid input. Please enter y for Yes or n for No: ')



    if retry_attempt=='y':
        user_retries=1
    elif retry_attempt=='n':
        user_retries=0
    else:





# #Collect User Destination Location Data for weather mapping 
# user_location_as_string=input('So, where are we today?\n Press 1 for Home or Press 2 for Work: ')
# user_location_as_int=int(user_location_as_string)

# #User weather selection confirmation message
# print('Great! We will now map the weather for ' + str(user_location_as_int))

# #Collect User Weather Data for weather mapping
# raining=int(input('Is it raining? Press 1 for Yes or Press 0 for No: '))

# #Programming Decision Logic for Weather Mapping
# if raining and user_location_as_int==1:
#     print('It is raining, stay home and do something fun! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')
# elif not raining and user_location_as_int==1:
#     print('It is not raining, and its safe to travel to work! The current temperature is ' + str(computer_weather) + ' degrees Fahrenheit.')