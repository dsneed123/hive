"""
Written by Davis Sneed
Started on 02/28/2026


Hive
==============================================================================
Hive is an AI-powered personal assistant designed to automate outreach,
manage email campaigns, and maximize promotion across social media platforms.

The system integrates:
- Intelligent email management and automated responses
- Social media growth optimization workflows
- Real-time analytics tracking and performance metrics
- An RGB LED matrix display for live system status and data visualization
- A web-based dashboard built with React for monitoring and control

This file serves as the main entry point for the Hive system, initializing
core services, analytics pipelines, automation engines, and external interfaces.
===============================================================================

**note** No AI was used in the creation of this program. All code was written by hand by Davis Sneed
"""
# Hive - Your AI Personal Assistant
def chat_mode():
    print("Entering Chat Mode...")

#function to control RGB lighting on devices
def rgb_mode():
    print("Entering RGB Mode...")

#function to configure Hive's settings and preferences
def configure():
    print("Entering Configure Mode...")

#function to display the help menu
def help_menu():
    print("""
    Chat Mode: This mode allows you to have a conversation with Hive. You can ask questions, get information, or just chat about anything you'd like.
    
    RGB Mode: This mode allows you to control the RGB lighting on your devices. You can change colors, set patterns, and customize your lighting experience.
    
    Configure: This mode allows you to configure Hive's settings and preferences. You can customize how Hive responds, set up integrations, and manage your account.
    
    Exit: This option will exit the program.
    """)

#function to exit the program
def exit_program():
    print("Exiting Hive. Goodbye!")
    exit()
#print the menu and options for the user to select from
def print_main_menu():
    print("""
    ^^      .-=-=-=-.  ^^
^^        (`-=-=-=-=-`)         ^^
        (`-=-=-=-=-=-=-`)  ^^         ^^
  ^^   (`-=-=-=-=-=-=-=-`)   ^^                            ^^
      ( `-=-=-=-(@)-=-=-` )      ^^
      (`-=-=-=-=-=-=-=-=-`)  ^^
      (`-=-=-=-=-=-=-=-=-`)              ^^
      (`-=-=-=-=-=-=-=-=-`)                      ^^
      (`-=-=-=-=-=-=-=-=-`)  ^^
       (`-=-=-=-=-=-=-=-`)          ^^
        (`-=-=-=-=-=-=-`)  ^^                 ^^
    jgs   (`-=-=-=-=-`)
           `-=-=-=-=-`
------------------------------------------------
welcome to Hive. Your ai personal assistant. Enter a mode to get started. Type 'help' for more information on each mode.
          [1] Chat Mode
          [2] RGB Mode
          [3] Configure
          [4] help
          [5] exit
          """)
def main():
    print_main_menu()

#initialize the main function
if __name__ == "__main__":
    main()