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
from dotenv import load_dotenv
import os
import subprocess
import webbrowser
import time
import signal
import sys
from src.analytics import get_tiktok_analytics
from src.Chat_Mode import claude_chat_mode

# Hive - Your AI Personal Assistant
def chat_mode():
    print("Entering Chat Mode...")
    api_key = os.getenv("CLAUDE_KEY")
    TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME")
    TIKTOK_URL = os.getenv("TIKTOK_URL")
    message = input("You: ")
    account_raw_data = get_tiktok_analytics(TIKTOK_URL)
    claude_chat_mode(api_key, message, TIKTOK_USERNAME, account_raw_data)

#function to control RGB lighting on devices
def rgb_mode():
    print("Entering RGB Mode...")
    from src.rgb_controller import HiveRGBController
    controller = HiveRGBController()
    controller.setup()
    print("RGB display started. Press Ctrl+C to stop.")
    try:
        controller.run()
    except KeyboardInterrupt:
        controller.stop()

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

def web_interface():
    print("Starting Hive Web Interface...")

    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "src", "web_interface")

    # Start FastAPI backend (use venv python if available)
    venv_python = os.path.join(project_root, "venv", "bin", "python3")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    backend = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "src.api.server:app", "--reload", "--port", "8001"],
        cwd=project_root,
    )
    print("  Backend started on http://localhost:8001")

    # Start Next.js frontend
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
    )
    print("  Frontend started on http://localhost:3000")

    # Give the servers a moment to boot, then open the browser
    time.sleep(3)
    webbrowser.open("http://localhost:3000")
    print("  Browser opened. Press Ctrl+C to stop the servers.\n")

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n  Shutting down servers...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("  Servers stopped.")
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
          [5] web interface
          [4] help
          [6] exit
          """)
def main():
    load_dotenv()  # Load environment variables from .env file
    print_main_menu()
    selection = input("Enter your selection: ")
    menu = {
        "1": chat_mode,
        "2": rgb_mode,
        "3": configure,
        "4": help_menu,
        "5": web_interface,
        "6": exit_program
    }
    while True:
        if selection in menu:
            menu[selection]()
        else:
            print("Invalid selection. Please try again.")
        selection = input("Enter your selection: ")


#initialize the main function
if __name__ == "__main__":
    main()