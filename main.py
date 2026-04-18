while True:
    name = input("\nEnter your name: ")

    print("\nHello", name + "! Welcome to Career Guide System")

    print("\nWhat are you interested in?")
    print("1. Technology")
    print("2. Creativity")
    print("3. Business")

    choice = input("\nEnter your choice (1/2/3): ")

    print("\nAnalyzing your interest...\n")

    if choice == "1":
        print("Great choice,", name + "!")
        print("Suggested careers:")
        print("- Software Developer")
        print("- Data Scientist")

    elif choice == "2":
        print("Awesome,", name + "!")
        print("Suggested careers:")
        print("- UI/UX Designer")
        print("- Graphic Designer")

    elif choice == "3":
        print("Nice,", name + "!")
        print("Suggested careers:")
        print("- Business Analyst")
        print("- Marketing Manager")

    else:
        print("Invalid choice. Please select 1, 2, or 3.")

    again = input("\nDo you want to try again? (yes/no): ")

    if again.lower() != "yes":
        print("\nThank you for using Career Guide System. Goodbye!")
        break



