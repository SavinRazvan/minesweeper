import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        """
        Initialize game board with given dimensions and mine count.
        """

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly until we have the required number of mines
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()


    def print(self):
        """
        Prints a text-based representation of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")


    def is_mine(self, cell):
        """
        Checks if a given cell is a mine.
        """
        i, j = cell
        return self.board[i][j]


    def nearby_mines(self, cell):
        """
        Returns the number of mines that are within one row and column of a given cell, not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is a mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count


    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines



class Sentence():
    """
    Logical statement about a Minesweeper game.
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        """
        Checks if two sentences are logically equivalent.
        """
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        """
        Returns a string representation of the sentence.
        """
        return f"{self.cells} = {self.count}"


    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # If the count matches the number of cells, all cells are known to be mines
        if self.count == len(self.cells):
            return self.cells
        return None


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # If the count is 0, all cells are known to be safe
        if self.count == 0:
            return self.cells
        return None


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that a cell is known to be a mine.
        """

        # If the cell is in self.cells, remove it and update the count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that a cell is known to be safe.
        """

        # If the cell is in self.cells, remove it
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        """
        Initialize the AI player with given board dimensions.
        """

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []


    def mark_mine(self, cell):
        """
        Marks a cell as a mine and updates all knowledge to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)


    def mark_safe(self, cell):
        """
        Marks a cell as safe and updates all knowledge to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given safe cell, how many neighboring cells have mines in them.

        This function should:
            1) Mark the cell as a move that has been made
            2) Mark the cell as safe
            3) Add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
            4) Mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
            5) Add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # Initialize a set to store undetermined cells around the current cell
        undetermined_cells = set()

        # Loop over all cells within one row and column of the current cell
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Check if the cell is in bounds and has unknown state (not marked as mine or safe)
                if 0 <= i < self.height and 0 <= j < self.width:
                    check_cell = (i, j)

                    # Add cells with unknown state to the undetermined_cells set
                    if check_cell not in self.moves_made and check_cell not in self.mines:
                        undetermined_cells.add(check_cell)

                    # If the cell is a mine, reduce the count by 1
                    elif check_cell in self.mines:
                        count -= 1

        # 3) Add a new sentence to the AI's knowledge base based on the value of cell and count
        new_sentence = Sentence(undetermined_cells, count)
        self.knowledge.append(new_sentence)

        # 4) Mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            # Check for safes and mines after we have the new sentence in the knowledge base
            check_new_safes = sentence.known_safes()
            if check_new_safes is not None:
                for cell in check_new_safes.copy():
                    # Mark the new safe cell as safe
                    self.mark_safe(cell)

            check_new_mines = sentence.known_mines()
            if check_new_mines is not None:
                for cell in check_new_mines.copy():
                    # Mark the new mine cell as a mine
                    self.mark_mine(cell)

        # 5) Add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        for sentence_one in self.knowledge:
            for sentence_two in self.knowledge:
                # Take pairs of sentences; skip the first one to avoid comparing to itself
                if sentence_one is sentence_two:
                    continue

                # Check for duplicates in the knowledge base
                if sentence_one == sentence_two:
                    self.knowledge.remove(sentence_two)

                # Check if sentence_one is a subset of sentence_two and make an inference
                elif sentence_one.cells.issubset(sentence_two.cells):
                    update_sentence = Sentence((sentence_two.cells - sentence_one.cells), (sentence_two.count - sentence_one.count))
                    # Add the new sentence only if it is new (avoid duplicates)
                    if update_sentence not in self.knowledge:
                        self.knowledge.append(update_sentence)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move that has been made.

        This function may use the knowledge in self.mines, self.safes, and self.moves_made, but should not modify any of those values.
        """

        # Calculate the set of safe moves that have not been made
        safe_moves = self.safes - self.moves_made

        # If there are safe moves available, randomly choose one and return it
        if safe_moves:
            return random.choice(tuple(safe_moves))

        # If no safe move is available, return None
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) Have not already been chosen, and
            2) Are not known to be mines
        """
        # Check if the board is full. If all cells have been chosen, return None.
        if (len(self.mines) + len(self.moves_made)) == (self.height * self.width):
            return None

        # Create a list to store available moves
        available_moves = []

        # Loop through all cells on the board
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)

                # Check if the cell has not been chosen and is not a mine
                if cell not in self.moves_made and cell not in self.mines:
                    available_moves.append(cell)

        # If there are available moves, randomly choose one and return it
        if available_moves:
            return random.choice(available_moves)

        # If no random move is possible, return None
        return None
