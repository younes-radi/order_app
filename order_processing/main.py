"""
Main entry point for the order processing application.

This module initializes the application GUI and sets up the required components.
"""
import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from controllers.application_controller import ApplicationController
from views.main_window import MainWindow
from utils.database import init_database, seed_default_data

def main():
    """Initialize and run the application."""
    # Create data directories if they don't exist
    os.makedirs("data", exist_ok=True)
    
    # Initialize the application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a consistent look across platforms
    
    # Create the application controller
    controller = ApplicationController()
    
    # Create and show the main window
    window = MainWindow(controller)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()