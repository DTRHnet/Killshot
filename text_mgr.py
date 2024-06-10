import shutil

class TermUtil:
    @staticmethod
    def getTermWidth():
        """
        Function to get the width of the terminal in columns.
        :return: Width of the terminal in columns.
        """
        return shutil.get_terminal_size().columns
    
    @staticmethod
    def hLine(char, height=1):
        """
        Function to print a horizontal line of a specified character.
        :param char: Character to be used for the line.
        :param height: Height of the line (number of rows).
        """
        term_width = TermUtil.getTermWidth()
        for _ in range(height):
            print(char * term_width)
    
    @staticmethod
    def hTitle(string, position='center', char='-'):
        """
        Function to print a title string with a horizontal line.
        :param string: String to be displayed as the title.
        :param position: Position of the string ('left', 'center', or 'right').
        :param char: Character to be used for the horizontal line.
        """
        term_width = TermUtil.getTermWidth()
        string_length = len(string)
        remaining_width = term_width - string_length - 4  # 4 accounts for padding and line characters

        if position == 'left':
            print(f"{string} {char * remaining_width}")
        elif position == 'center':
            left_padding = (remaining_width // 2) - 1
            right_padding = remaining_width - left_padding
            print(f"{char * left_padding} {string} {char * right_padding}")
        elif position == 'right':
            print(f"{char * remaining_width} {string}")
        else:
            print("Invalid position specified. Please use 'left', 'center', or 'right'.")

# Example usage
TermUtil.hTitle("Testing logger()", position='center', char='#')
