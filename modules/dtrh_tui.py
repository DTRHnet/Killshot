import curses
from menu_manager import MenuManager

class TUI:
    def __init__(self, menu_data):
        self.menu_data = menu_data
        self.current_selection = 0
        self.menu_stack = [menu_data]
        self.menu_titles = ["Main Menu"]

    def draw_menu(self, stdscr):
        """
        Draws the menu using curses.
        :param stdscr: The curses screen object.
        """
        stdscr.clear()
        current_menu = self.menu_stack[-1]
        menu_title = self.menu_titles[-1]
        
        # Print the menu title
        stdscr.addstr(0, 0, menu_title, curses.A_BOLD)
        
        for idx, item in enumerate(current_menu.keys()):
            if idx == self.current_selection:
                stdscr.addstr(idx + 1, 0, f"> {item}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f"  {item}")

        stdscr.refresh()

    def navigate_menu(self, stdscr):
        """
        Handles menu navigation.
        :param stdscr: The curses screen object.
        """
        while True:
            self.draw_menu(stdscr)
            key = stdscr.getch()

            if key == curses.KEY_UP and self.current_selection > 0:
                self.current_selection -= 1
            elif key == curses.KEY_DOWN and self.current_selection < len(self.menu_stack[-1]) - 1:
                self.current_selection += 1
            elif key == curses.KEY_RIGHT or key == curses.KEY_ENTER or key in [10, 13]:
                selected_item = list(self.menu_stack[-1].keys())[self.current_selection]
                if isinstance(self.menu_stack[-1][selected_item], dict):
                    self.menu_stack.append(self.menu_stack[-1][selected_item])
                    self.menu_titles.append(selected_item)
                    self.current_selection = 0
            elif key == curses.KEY_LEFT and len(self.menu_stack) > 1:
                self.menu_stack.pop()
                self.menu_titles.pop()
                self.current_selection = 0
            elif key == ord('q'):
                break

def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.keypad(True)  # Enable keypad mode
    menu_data = MenuManager.read_menu_from_json('menu.json')
    tui = TUI(menu_data)
    tui.navigate_menu(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
