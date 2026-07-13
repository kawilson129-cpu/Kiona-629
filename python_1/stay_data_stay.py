print("""


                       ███████╗████████╗ █████╗ ██╗   ██╗    ██████╗  █████╗ ████████╗ █████╗     ███████╗████████╗ █████╗ ██╗   ██╗
                       ██╔════╝╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ██╔════╝╚══██╔══╝██╔══██╗╚██╗ ██╔╝
                       ███████╗   ██║   ███████║ ╚████╔╝     ██║  ██║███████║   ██║   ███████║    ███████╗   ██║   ███████║ ╚████╔╝ 
                       ╚════██║   ██║   ██╔══██║  ╚██╔╝      ██║  ██║██╔══██║   ██║   ██╔══██║    ╚════██║   ██║   ██╔══██║  ╚██╔╝  
                       ███████║   ██║   ██║  ██║   ██║       ██████╔╝██║  ██║   ██║   ██║  ██║    ███████║   ██║   ██║  ██║   ██║   
                       ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   
                                                                                                          

                                           _____ __                 ____        __           _____ __             
                                          / ___// /_____ ___  __   / __ \____ _/ /_____ _   / ___// /_____ ___  __
                                          \__ \/ __/ __ `/ / / /  / / / / __ `/ __/ __ `/   \__ \/ __/ __ `/ / / /
                                         ___/ / /_/ /_/ / /_/ /  / /_/ / /_/ / /_/ /_/ /   ___/ / /_/ /_/ / /_/ /     
                                        /____/\__/\__,_/\__, /  /_____/\__,_/\__/\__,_/   /____/\__/\__,_/\__, /  
                                                       /____/                                            /____/                                                                                                                                                               

                                                                    STAY DATA STAY
                                             ============================================================
                                                           Privacy Protection for Travelers
                                             ============================================================

                                                Initializing security...

                                                ✓ Loading user profile
                                                ✓ Preparing vacation session
                                                ✓ Secure tracking enabled

                                             ------------------------------------------------------------
                                                This application helps prevent unauthorized access to your
                                                online accounts by reminding you to log out before checkout.

                                                Stay secure.
                                                Stay protected.
                                                Stay Data Stay.
                                             ------------------------------------------------------------
""")
input("Press Enter to log in...")

#Hardcoded credentials/log in
correct_username='KW_Data'
correct_password='StayData123!'

#Ask user for credentials
user_name=input('Please enter your username: ')
user_password=input(('Thank You ')+user_name+'! Please enter your password: ')

#Error handling for incorrect credentials
while user_name !=correct_username or user_password !=correct_password:
    #Stop user if one of the login credentials is incorrect
    print('The incorrect credentials have been provided. Please try again.')
    user_name=input('Please enter your username: ')
    user_password=input(('Thank You ')+user_name+'! Please enter your password: ')

#Show user the start message
print("Welcome " + user_name + " to Stay Data Stay, where your data stays with you and does not get left behind! Let's get started!")

#Ask user if they are currently on vacation/staying somewhere/and answers Yes/New trip log attempt
trip_status = input("Are you currently on a trip or hotel stay?\n\nPress 1 for Yes\nPress 0 for No\n\nChoice: ")
if trip_status == "1":
    print("\nExcellent! Let's begin by recording your stay.\n")
    hotel_name = input("Hotel Name: ").strip()
    room_number = input("Room Number: ").strip()
    while room_number == "":
        print("\nRoom number cannot be left blank.")
        room_number = input("Please enter your room number: ").strip()
    days_staying = int(input("How many nights will you be staying: "))

#User answers No
elif trip_status == "0":
    print("\nNo active trip found. You can create one anytime.\n")

else:
    print("\nInvalid entry. Please restart and enter either 1 or 0.\n")

if confirmation == "1":
    print("\nExcellent! Your trip has been successfully recorded.")

elif confirmation == "2":
    print("\nNo problem! Let's update your information.")
    edit_choice = input(
"\nWhat would you like to update?\n"
"1 - Hotel Name\n"
"2 - Room Number\n"
"3 - Length of Stay\n\n"
"Choice: "
).strip()

#Error handling for invalid entry
if edit_choice == "1":
    hotel_name = input("Enter your corrected hotel name: ").strip()

elif edit_choice == "2":
    room_number = input("Enter your corrected room number: ").strip()

elif edit_choice == "3":
    days_staying = int(input("Enter your corrected number of days: "))

else:
    print("\nInvalid entry.")
confirmed=False

while not confirmed:
    print("\n" + "=" * 45)
    print("             STAY SUMMARY")
    print("=" * 45)

    print("🏨 Hotel Name:      ", hotel_name)
    print("🛏️  Room Number:     ", room_number)
    print("📅 Length of Stay:  ", days_staying, "days")

    print("=" * 45)

    confirmation = input(
    "\nIs all of the above information correct?\n\n"
    "Press 1 for Yes\n"
    "Press 2 for No\n\n"
    "Choice: "
    ).strip()


#If No, show message: “No stay detected. You’re all clear!” Then jump to Step #16.
#If Yes, continue to Step #7.



#Ask user to enter the number of days for their stay
#Example: “How many days will you be staying?”


#Ask user to enter the accounts they logged into
#Examples: Netflix, Hulu, Prime Video, YouTube, Spotify, hotel Wi-Fi, email, gaming accounts, etc.



#Store the logged-in account list



# Display summary of entered accounts
# Example: “You logged into: Netflix, Prime Video, YouTube.”



#Ask user when they would like to receive additional reminder notifications
#Second to last day of the final trip date
#Third to the last day of the final trip date
#Fourth to the last day of the final trip date
#Fifth to the last day of the final trip date
#Display Stay Data Stay trip log confirmation message


#Track the stay duration


#Depending on the user’s additional reminders selected, send notifications based on the options chosen. 


#While: The user has initiated multiple alerts...
#If: The notifications will continue to loop an alert message that includes a trip day countdown


#Else: One alert is sent on the last day of the final trip date On the final day of the stay, send reminder notification 
# Example: “Reminder: You logged into Netflix, Prime Video, and YouTube. Please log out before leaving.”


#Show user’s logged list and ask user to confirm they logged out 
# Example: “Have you logged out of all accounts?”


#User confirms logout
#If Yes, show success message.


#If No, repeat reminder and show account list again.


#Display closing message 
# Example: “Thanks for using Stay Data Stay — now you can leave in peace, and your data won’t stay behind!”


#Show farewell message
print('Thank you for using Stay Data Stay!\nHelping you leave with memories and not without your data!')

#Stop the program