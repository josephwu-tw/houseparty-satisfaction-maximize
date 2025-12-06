"""
Base menu class with shared utilities.
"""
from abc import ABC, abstractmethod
from utils import print_header, print_section, wait_for_key, get_user_input


class BaseMenu(ABC):
    """Base class for all menu handlers."""
    
    def __init__(self, friend_repo, food_repo):
        self.friend_repo = friend_repo
        self.food_repo = food_repo
    
    @abstractmethod
    def display(self):
        """Display menu options."""
        pass
    
    @abstractmethod
    def handle_choice(self, choice: str) -> bool:
        """
        Handle user choice.
        Returns False to exit menu, True to continue.
        """
        pass
    
    def run(self):
        """Main menu loop."""
        while True:
            self.display()
            choice = input("\nChoice: ").strip()
            if not self.handle_choice(choice):
                break
    
    def show_error(self, message: str):
        """Display error message."""
        print(f"❌ {message}")
        wait_for_key()
    
    def show_success(self, message: str):
        """Display success message."""
        print(f"✓ {message}")
    
    def confirm(self, message: str) -> bool:
        """Get yes/no confirmation."""
        response = input(f"{message} (y/n): ").strip().lower()
        return response == 'y'
    
    def get_input_with_default(self, prompt: str, default, cast_type=str):
        """Get input with a default value."""
        user_input = input(f"{prompt} [default: {default}]: ").strip()
        if not user_input:
            return default
        try:
            return cast_type(user_input)
        except ValueError:
            print(f"⚠️ Invalid input, using default: {default}")
            return default