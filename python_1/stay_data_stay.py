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

#Invalid attempts counter to limit the number of incorrect entries
invalid_attempts = 0
trip_status = ""

while invalid_attempts < 3:

    trip_status = input(
        "Are you currently on a trip or hotel stay?\n\n"
        "Press 1 for Yes\n"
        "Press 0 for No\n\n"
        "Choice: ").strip()

    if trip_status in ("0", "1"):
        break

    invalid_attempts += 1

    if invalid_attempts < 3:
        print(
            "\nInvalid entry."
            "\nPlease enter either 1 or 0.")

        print(
            "Attempts remaining:",
            3 - invalid_attempts)

# Ask user if they are currently on vacation or staying somewhere

trip_status = input(
    "Are you currently on a trip or hotel stay?\n\n"
    "Press 1 for Yes\n"
    "Press 0 for No\n\n"
    "Choice: ").strip()

if trip_status == "1":
    print("\nExcellent! Let's begin by recording your stay.\n")

    # Collect hotel name
    hotel_name = input("Hotel Name: ").strip()

    while hotel_name == "":
        print("\nHotel name cannot be left blank.")
        hotel_name = input("Please enter your hotel name: ").strip()

    # Collect room number
    room_number = input("Room Number: ").strip()

    while room_number == "":
        print("\nRoom number cannot be left blank.")
        room_number = input("Please enter your room number: ").strip()

    # Collect length of stay
    while True:
        try:
            days_staying = int(
                input("How many nights will you be staying: ").strip())

            if days_staying > 0:
                break
            else:
                print("\nPlease enter a number greater than 0.")

        except ValueError:
            print("\nPlease enter the number of nights using digits.")

    # Keep showing the summary until the user confirms it
    confirmed = False

    while not confirmed:
        print("\n" + "=" * 45)
        print("             STAY SUMMARY")
        print("=" * 45)

        print("🏨 Hotel Name:      ", hotel_name)
        print("🛏️  Room Number:     ", room_number)
        print("📅 Length of Stay:  ", days_staying, "nights")

        print("=" * 45)

        confirmation = input(
            "\nIs all of the above information correct?\n\n"
            "Press 1 for Yes\n"
            "Press 2 for No\n\n"
            "Choice: ").strip()

        if confirmation == "1":
            confirmed = True
            print("\nExcellent! Your trip has been successfully recorded.")

        elif confirmation == "2":
            edit_choice = input(
                "\nWhat would you like to update?\n"
                "1 - Hotel Name\n"
                "2 - Room Number\n"
                "3 - Length of Stay\n\n"
                "Choice: ").strip()

            if edit_choice == "1":
                hotel_name = input(
                    "Enter your corrected hotel name: ").strip()

                while hotel_name == "":
                    print("\nHotel name cannot be left blank.")
                    hotel_name = input(
                        "Please enter your hotel name: ").strip()

            elif edit_choice == "2":
                room_number = input(
                    "Enter your corrected room number: ").strip()

                while room_number == "":
                    print("\nRoom number cannot be left blank.")
                    room_number = input(
                        "Please enter your room number: ").strip()

            elif edit_choice == "3":
                while True:
                    try:
                        days_staying = int(
                            input(
                                "Enter your corrected number of nights: "
                            ).strip())

                        if days_staying > 0:
                            break
                        else:
                            print(
                                "\nPlease enter a number greater than 0.")

                    except ValueError:
                        print(
                            "\nPlease enter the number of nights using digits.")

            else:
                print(
                    "\nInvalid edit selection. "
                    "Please choose 1, 2, or 3.")

        else:
            print(
                "\nInvalid confirmation entry. "
                "Please enter 1 or 2.")

    # The next part of your program goes here
    print("\nLet's continue to log your account activity.")

    # Store the available account choices in a dictionary
    account_options = {
        "1": "Netflix",
        "2": "YouTube",
        "3": "Amazon Prime Video",
        "4": "Hulu",
        "5": "Disney+",
        "6": "HBO Max",
        "7": "Peacock",
        "8": "Spotify",
        "9": "Apple TV+",
        "10": "Google / Gmail",
        "11": "Hotel Wi-Fi",
        "12": "Gaming Account",
        "13": "Other"
    }

    print("\n" + "=" * 60)
    print("             ACCOUNT ACTIVITY LOG")
    print("=" * 60)

    print("\nSelect every account you have logged into during your stay.")
    print("Enter multiple numbers separated by commas.")
    print("Example: 1, 2, 5, 10\n")

    for number, account_name in account_options.items():
        print(number + " - " + account_name)

    print("=" * 60)

    accounts_confirmed = False

    while not accounts_confirmed:


        user_selections = input(
            "\nEnter your account selections: ").strip()

        # Separate the numbers wherever the user entered a comma
        selected_numbers = user_selections.split(",")

        # This list will store the selected account names
        logged_accounts = []

        # This list will store invalid selections
        invalid_selections = []

        for number in selected_numbers:
            number = number.strip()

            if number in account_options:

                # Do not immediately add "Other"
                if number != "13":
                    account_name = account_options[number]

                # Prevent the same account from being added twice
                if account_name not in logged_accounts:
                    logged_accounts.append(account_name)

            else:
                invalid_selections.append(number)

        # Tell the user if any selection was invalid
        while invalid_selections:
            print(
                "\nInvalid selection(s): "
                + ", ".join(invalid_selections))
            print("Please choose only numbers from the account menu.")
            continue

        # Check whether the user selected Other
        if "13" in [number.strip() for number in selected_numbers]:

            adding_other_accounts = True

            while adding_other_accounts:
                other_account = input(
                    "\nEnter the name of the other account: ").strip()

                if other_account == "":
                    print("The account name cannot be blank.")

            
                if other_account not in logged_accounts:
                    logged_accounts.append(other_account)

                    another_account = input(
                        "\nWould you like to add another account?\n\n"
                        "Press 1 for Yes\n"
                        "Press 0 for No\n\n"
                        "Choice: ").strip()

                    if another_account == "0":
                        adding_other_accounts = False

                    elif another_account != "1":
                        print(
                            "\nInvalid entry. "
                            "Returning to your account summary.")
                        adding_other_accounts = False

        # Make sure the user selected at least one account
        while len(logged_accounts) == 0:
            print(
                "\nNo accounts were selected. "
                "Please choose at least one account.")
            continue

        # Display the account summary
        print("\n" + "=" * 60)
        print("              LOGGED ACCOUNT SUMMARY")
        print("=" * 60)

        for account_number, account_name in enumerate(
            logged_accounts,
            start=1):
            print(
                str(account_number)
                + ". "
                + account_name)

        print("=" * 60)


        account_confirmation = input(
            "\nIs this account list correct?\n\n"
            "Press 1 for Yes\n"
            "Press 2 to Select Again\n\n"
            "Choice: ").strip()

        if account_confirmation == "1":
            accounts_confirmed = True

            print(
                "\nExcellent! Your account activity "
                "has been successfully recorded.")

        elif account_confirmation == "2":
            print(
                "\nNo problem. Let's rebuild your account list.")

        else:
            print(
                "\nInvalid confirmation entry. "
                "Please enter 1 or 2.")
#Kay's competency line message print("Everythign's working. Continue from here.")

    # REMINDER NOTIFICATION PREFERENCES

    print("\n" + "=" * 60)
    print("           REMINDER NOTIFICATION SETUP")
    print("=" * 60)

    print(
        "\nYou will automatically receive a logout reminder "
        "on the final day of your stay.")

    print(
        "\nYou may also select additional reminders "
        "for extra peace of mind.")

    # Store the optional reminder choices
    reminder_options = {
        "1": {
            "name": "Second-to-last day",
            "days_remaining": 2
        },
        "2": {
            "name": "Third-to-last day",
            "days_remaining": 3
        },
        "3": {
            "name": "Fourth-to-last day",
            "days_remaining": 4
        },
        "4": {
            "name": "Fifth-to-last day",
            "days_remaining": 5
        }
    }

    reminders_confirmed = False

    while not reminders_confirmed:

        print("\nAvailable Additional Reminders:\n")

        # Only show reminder options that fit within the trip length
        available_reminder_numbers = []

        for number, reminder_information in reminder_options.items():

            reminder_day = reminder_information["days_remaining"]

            if reminder_day <= days_staying:
                print(
                    number
                    + " - "
                    + reminder_information["name"])

                available_reminder_numbers.append(number)

        print("0 - No additional reminders")

        print("\nEnter multiple numbers separated by commas.")
        print("Example: 1, 2, 4")

        reminder_input = input(
            "\nSelect your reminder preference(s): "
        ).strip()

        # User selected no optional reminders
        if reminder_input == "0":
            selected_reminders = []
            reminders_confirmed = True

            print(
                "\nNo additional reminders selected.")

            print(
                "Your final-day reminder is still active.")

        else:
            selected_reminder_numbers = reminder_input.split(",")

            selected_reminders = []
            invalid_reminders = []

            for number in selected_reminder_numbers:
                number = number.strip()

                if number in available_reminder_numbers:

                    reminder_day = reminder_options[number][
                        "days_remaining"]

                    # Prevent duplicate reminder selections
                    if reminder_day not in selected_reminders:
                        selected_reminders.append(reminder_day)

                else:
                    invalid_reminders.append(number)

            if invalid_reminders:
                print(
                    "\nInvalid reminder selection(s): "
                    + ", ".join(invalid_reminders))

                print(
                    "Please select only the options currently shown.")

            elif len(selected_reminders) == 0:
                print(
                    "\nPlease select at least one reminder "
                    "or enter 0.")

            else:
                # Sort reminders from earliest alert to latest alert
                selected_reminders.sort(reverse=True)

                print("\n" + "=" * 60)
                print("          SELECTED REMINDER SUMMARY")
                print("=" * 60)

                for reminder_day in selected_reminders:

                    if reminder_day == 2:
                        print("✓ Second-to-last day reminder")

                    elif reminder_day == 3:
                        print("✓ Third-to-last day reminder")

                    elif reminder_day == 4:
                        print("✓ Fourth-to-last day reminder")

                    elif reminder_day == 5:
                        print("✓ Fifth-to-last day reminder")

                print("✓ Final-day reminder — automatically included")
                print("=" * 55)

                reminder_confirmation = input(
                    "\nAre these reminder choices correct?\n\n"
                    "Press 1 for Yes\n"
                    "Press 2 to Select Again\n\n"
                    "Choice: "
                ).strip()

                if reminder_confirmation == "1":
                    reminders_confirmed = True

                    print(
                        "\nExcellent! Your reminder schedule "
                        "has been saved.")

                    # COMPLETE TRIP AND REMINDER SUMMARY

                    print("\n" + "=" * 60)
                    print("              STAY DATA STAY SUMMARY")
                    print("=" * 60)

                    print("\n🏨 VACATION INFORMATION")
                    print("-" * 60)
                    print("Hotel Name:        ", hotel_name)
                    print("Room Number:       ", room_number)
                    print("Length of Stay:    ", days_staying, "nights")

                    print("\n🔐 ACCOUNTS LOGGED IN")
                    print("-" * 60)

                    for account_name in logged_accounts:
                        print("• " + account_name)

                    print("\n🔔 NOTIFICATION SCHEDULE")
                    print("-" * 60)

                    if len(selected_reminders) == 0:
                        print("• No additional reminders selected.")

                    else:
                        for reminder_day in selected_reminders:

                            if reminder_day == 2:
                                print("🔔 Second-to-last day reminder")

                            elif reminder_day == 3:
                                print("🔔 Third-to-last day reminder")

                            elif reminder_day == 4:
                                print("🔔 Fourth-to-last day reminder")

                            elif reminder_day == 5:
                                print("🔔 Fifth-to-last day reminder")

                    # Final-day reminder is always included
                    print("🔔 Final-day checkout reminder — automatically included")

                    print("\n" + "=" * 60)
                    print("Your trip and reminder preferences have been saved.")
                    print("Stay secure. Stay protected. Stay Data Stay.")
                    print("=" * 60)


                elif reminder_confirmation == "2":
                    print(
                        "\nNo problem. Let's rebuild "
                        "your reminder schedule.")

                else:
                    print(
                        "\nInvalid confirmation entry. "
                        "Please enter 1 or 2.")


                # =====================================================
                # REMINDER NOTIFICATION DEMONSTRATION
                # =====================================================

                print("\n" + "=" * 60)
                print("         🔔 UPCOMING STAY REMINDERS 🔔".center(60))
                print("=" * 60)

                print(
                    "\nPress Enter to view the reminders that were "
                    "scheduled for this stay.")

                input("\nPress Enter to continue...")

                # Display each optional reminder selected by the user
                for reminder_day in selected_reminders:

                    print("\n" + "-" * 60)

                    if reminder_day == 5:
                        print("🔔 FIFTH-TO-LAST DAY REMINDER".center(60))
                        print("\nYour checkout day is approaching.")

                    elif reminder_day == 4:
                        print("🔔 FOURTH-TO-LAST DAY REMINDER".center(60))
                        print("\nYou have four days remaining in your stay.")

                    elif reminder_day == 3:
                        print("🔔 THIRD-TO-LAST DAY REMINDER".center(60))
                        print("\nYou have three days remaining in your stay.")

                    elif reminder_day == 2:
                        print("🔔 SECOND-TO-LAST DAY REMINDER".center(60))
                        print("\nTomorrow is your final full day before checkout.")

                    print(
                        "\nPlease remember that you logged into "
                        "the following accounts:")

                    for account_name in logged_accounts:
                        print("• " + account_name)

                    print(
                        "\nMake sure you log out of all shared devices "
                        "before leaving.")

                    print("-" * 60)

                    input("\nPress Enter to view the next scheduled reminder...")

                # The final-day notification is always displayed
                print("\n" + "=" * 60)
                print("          🔔 FINAL-DAY NOTIFICATION 🔔".center(60))
                print("=" * 60)

                print("\nIt is the final day of your stay!")

                print(
                    "\nBefore checking out, please log out of "
                    "the following accounts:")

                for account_name in logged_accounts:
                    print("• " + account_name)

                print(
                    "\nLeave with your memories..."
                    "\nnot your data.")

                print("=" * 60)

                input("\nPress Enter to complete your trip...")

                # FINAL TRIP COMPLETION SCREEN

                input(
                    "\nPress Enter when your trip has come to an end...")

                print("\n" + "=" * 60)
                print("               ✈️ TRIP COMPLETE ✈️")
                print("=" * 60)

                print("\n🔔 FINAL STAY DATA STAY REMINDER")
                print("-" * 60)

                print(
                    "Your stay at "
                    + hotel_name
                    + " has come to an end.")

                print(
                    "\nBefore checking out, please remember to log out "
                    "of the following accounts:")
                
                for account_name in logged_accounts:
                    print("• " + account_name)

                print("\n" + "-" * 60)

                print("✓ Your trip information was recorded.")
                print("✓ Your account activity was reviewed.")
                print("✓ Your reminder preferences were saved.")
                print("✓ Your final-day logout reminder was delivered.")

                print("\n" + "=" * 60)
                print("              SESSION COMPLETE")
                print("=" * 60)

                print(
                    "\nThank you for using Stay Data Stay!")

                print(
                    "\nLeave with your memories..."
                    "\nand your data intact.")

                print(
                    "\nStay secure."
                    "\nStay protected."
                    "\nStay Data Stay.")

                print("\n" + "=" * 60)
            
if trip_status == "0":

    print("\n")
    print("=" * 60)
    print("STAY DATA STAY".center(60))
    print("=" * 60)

    print()
    print("✓ No Active Trip Detected".center(60))
    print()

    print("You're all set!".center(60))
    print()

    print(
        "Whenever you're planning your next vacation,".center(60))
    print(
        "we'll be here to help protect your accounts.".center(60))

    print()
    print("-" * 60)

    print("Travel with confidence.".center(60))
    print("Leave with memories...".center(60))
    print("and with your data intact.".center(60))

    print()
    print("Stay secure.".center(60))
    print("Stay protected.".center(60))
    print("Stay Data Stay.".center(60))

    print("-" * 60)

if invalid_attempts == 3:

    print("\n")
    print("=" * 60)
    print("         STAY DATA STAY".center(60))
    print("=" * 60)

    print()
    print("Maximum number of attempts reached.".center(60))
    print("This session has now ended.".center(60))

    print()
    print("Thank you for using Stay Data Stay!".center(60))

    print()
    print("Travel with confidence.".center(60))
    print("Leave with memories...".center(60))
    print("and with your data intact.".center(60))

    print()
    print("Stay secure.".center(60))
    print("Stay protected.".center(60))
    print("Stay Data Stay.".center(60))

    print("\n" + "=" * 60)
