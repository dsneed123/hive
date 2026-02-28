

def chat_mode():
    print("Entering Chat Mode...")

def rgb_mode():
    print("Entering RGB Mode...")

def configure():
    print("Entering Configure Mode...")

def help_menu():
    print("""
    Chat Mode: This mode allows you to have a conversation with Hive. You can ask questions, get information, or just chat about anything you'd like.
    
    RGB Mode: This mode allows you to control the RGB lighting on your devices. You can change colors, set patterns, and customize your lighting experience.
    
    Configure: This mode allows you to configure Hive's settings and preferences. You can customize how Hive responds, set up integrations, and manage your account.
    
    Exit: This option will exit the program.
    """)
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