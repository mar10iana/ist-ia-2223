# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 88:
# 95817 Lourenco Pacheco
# 99528 Mariana Mendonca

import numpy as np
import sys
import tracemalloc
import time
import copy
from search import (
    Problem,
    Node,
    InstrumentedProblem,
    depth_first_tree_search,
)

class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self):
        self.board = np.array([[None for i in range(11)] for j in range(11)])
        # self.invalid = False
        self.boat_count = [4, 3, 2, 1]
        self.hints = []
        self.hints_final = [] 
                
    def copy_state(self):
        
        new_board = Board()
        new_board.board = copy.deepcopy(self.board)
        new_board.boat_count = copy.deepcopy(self.boat_count)
        new_board.hints = copy.deepcopy(self.hints)
        new_board.hints_final = copy.deepcopy(self.hints_final)
        
        return new_board
    
    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def get_number_of_cells_left_row(self, row: int) -> int:
        """Devolve o número de células que faltam preencher na linha
        passada como argumento."""
        return self.board[row][10]
    
    def get_number_of_cells_left_col(self, col: int) -> int:
        """Devolve o número de células que faltam preencher na coluna
        passada como argumento."""
        return self.board[10][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.get_value(row, col + 1), self.get_value(row, col - 1))
    
    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def set_value(self, row: int, col: int, value):
        """Atribui o valor na respetiva posição do tabuleiro."""
        self.board[row][col] = value
        if value == 'W':
            return
        elif self.board[row][10] != None and self.board[10][col] != None:
            self.board[row][10] -= 1
            self.board[10][col] -= 1
        

    def set_boat(self, action):
        row = action[0] 
        col = action[1]
        size = action[2]
        orientation = action[3]

        self.boat_count[size-1] -= 1
        
        if(size == 1):
            self.set_value(row, col, 'c')
            return
        
        if orientation == 'V':
            self.set_value(row, col, 't')
            for i in range(size-2):
                self.set_value(row + i + 1, col, 'm')
            self.set_value(row + size - 1, col, 'b')
            return
        
        if orientation == 'H':
            self.set_value(row, col, 'l')
            for i in range(size-2):
                self.set_value(row, col + i + 1, 'm')
            self.set_value(row, col + size - 1, 'r')
            return
        

    def check_if_ship_fits(self, i: int, j: int, boat_size: int, orientation: str):

        if j < 0 or j > 9 or i < 0 or i > 9:
            return False

        if boat_size == 1:
            
            if self.board[i][10] == 0 or self.board[10][j] == 0:
                return False

            if self.board[i][j] != None:
                return False

            if i != 0:
                if self.board[i-1][j] != None and self.board[i-1][j] != "W":
                    return False
                if j != 0:
                    if self.board[i-1][j-1] != None and self.board[i-1][j-1] != "W":
                        return False
                if j != 9:
                    if self.board[i-1][j+1] != None and self.board[i-1][j+1] != "W":
                        return False

            if i != 9:
                if self.board[i+1][j] != None and self.board[i+1][j] != "W":
                    return False
                if j != 0:
                    if self.board[i+1][j-1] != None and self.board[i+1][j-1] != "W":
                        return False
                if j != 9:
                    if self.board[i+1][j+1] != None and self.board[i+1][j+1] != "W":
                        return False

            if j != 0:
                if self.board[i][j-1] != None and self.board[i][j-1] != "W":
                    return False
            if j != 9:
                if self.board[i][j+1] != None and self.board[i][j+1] != "W":
                    return False
        
        if orientation == 'H':

            if j + boat_size > 10:
                return False

            if self.get_number_of_cells_left_row(i) < boat_size:
                return False

            for k in range(boat_size):
                if self.get_number_of_cells_left_col(j+k) == 0:
                    return False

            if j != 0:
                if self.board[i][j-1] != None and self.board[i][j-1] != "W":
                    return False

            if j + boat_size != 10:
                if self.board[i][j+boat_size] != None and self.board[i][j+boat_size] != "W":
                    return False
                    
            for k in range(boat_size):
                if self.board[i][j+k] != None:
                    return False

            if j == 0:
                for k in range(boat_size+1):
                    if i != 0:
                        if self.board[i-1][j+k] != None and self.board[i-1][j+k] != "W":
                            return False
                    if i != 9:
                        if self.board[i+1][j+k] != None and self.board[i+1][j+k] != "W":
                            return False

            elif j + boat_size == 10:
                for k in range(-1, boat_size):
                    if i != 0:
                        if self.board[i-1][j+k] != None and self.board[i-1][j+k] != "W":
                            return False
                    if i != 9:
                        if self.board[i+1][j+k] != None and self.board[i+1][j+k] != "W":
                            return False
            else:
                for k in range(-1, boat_size+1):
                    if i != 0:
                        if self.board[i-1][j+k] != None and self.board[i-1][j+k] != "W":
                            return False
                    if i != 9:
                        if self.board[i+1][j+k] != None and self.board[i+1][j+k] != "W":
                            return False

        if orientation == 'V':
            if i + boat_size > 10:
                return False

            if self.get_number_of_cells_left_col(j) < boat_size:
                return False

            for k in range(boat_size):
                if self.get_number_of_cells_left_row(i+k) == 0:
                    return False

            if i != 0:
                if self.board[i-1][j] != None and self.board[i-1][j] != "W":
                    return False
    
            if i + boat_size != 10:
                if self.board[i+boat_size][j] != None and self.board[i+boat_size][j] != "W":
                    return False
    
            for k in range(boat_size):
                if self.board[i+k][j] != None:
                    return False
                
            if i == 0:
                for k in range(boat_size+1):
                    if j != 0:
                        if self.board[i+k][j-1] != None and self.board[i+k][j-1] != "W":
                            return False
                    if j != 9:
                        if self.board[i+k][j+1] != None and self.board[i+k][j+1] != "W":
                            return False

            elif i + boat_size == 10:
                for k in range(-1, boat_size):
                    if j != 0:
                        if self.board[i+k][j-1] != None and self.board[i+k][j-1] != "W":
                            return False

                    if j != 9:
                        if self.board[i+k][j+1] != None and self.board[i+k][j+1] != "W":
                            return False
            else:
                for k in range(-1, boat_size+1):
                    if j != 0:
                        if self.board[i+k][j-1] != None and self.board[i+k][j-1] != "W":
                            return False
                    if j != 9:
                        if self.board[i+k][j+1] != None and self.board[i+k][j+1] != "W":
                            return False
        return True
        
    def place_size_four_ship(self):
        
        action_list = []
        
        if self.boat_count[3] == 0:
            return action_list

        for i in range(7):
            for j in range(10):
                if self.check_if_ship_fits(i, j, 4, 'V'):
                    action_list.append((i, j, 4, 'V'))
                if self.check_if_ship_fits(j, i, 4, 'H'):
                    action_list.append((j, i, 4, 'H'))
                    
        return action_list
                    
    def place_size_three_ship(self):
        
        action_list = []

        if self.boat_count[2] == 0:
            return action_list

        for i in range(8):
            for j in range(10):
                if self.check_if_ship_fits(i, j, 3, 'V'):
                    action_list.append((i, j, 3, 'V'))
                if self.check_if_ship_fits(j, i, 3, 'H'):
                    action_list.append((j, i, 3, 'H'))
                    
        return action_list
                    
    def place_size_two_ship(self):
        
        action_list = []

        if self.boat_count[1] == 0:
            return action_list

        for i in range(9):
            for j in range(10):
                if self.check_if_ship_fits(i, j, 2, 'V'):
                    action_list.append((i, j, 2, 'V'))
                if self.check_if_ship_fits(j, i, 2, 'H'):
                    action_list.append((j, i, 2, 'H'))
                    
        return  action_list
                    
    def place_size_one_ship(self):

        action_list = []

        if self.boat_count[0] == 0: 
            return action_list

        for i in range(10):
            for j in range(10):
                if self.check_if_ship_fits(i, j, 1, None):
                    action_list.append((i, j, 1, None))
                    
        return action_list

    def place_ships_hints(self):

        action_list = []
        
        for h in range(len(self.hints)):

            i = self.hints[h][0]
            j = self.hints[h][1]
                
            if self.hints[h][2] == "T":
                if self.check_if_ship_fits(i, j, 4, 'V'):
                    action_list.append((i, j, 4, "V"))

                if self.check_if_ship_fits(i, j, 3, 'V'):
                    action_list.append((i, j, 3, "V"))

                if self.check_if_ship_fits(i, j, 2, 'V'):
                    action_list.append((i, j, 2, "V"))

            if self.hints[h][2] == "B":

                if self.check_if_ship_fits(i-3, j, 4, 'V'):
                    action_list.append((i-3, j, 4, "V"))
                        
                if self.check_if_ship_fits(i-2, j, 3, 'V'):
                    action_list.append((i-2, j, 3, "V"))

                if self.check_if_ship_fits(i-1, j, 2, 'V'):                     
                    action_list.append((i-1, j, 2, "V"))
                    
            if self.hints[h][2] == "L":
                if self.check_if_ship_fits(i, j, 4, 'H'):
                    action_list.append((i, j, 4, "H"))
                        
                if self.check_if_ship_fits(i, j, 3, 'H'):
                    action_list.append((i, j, 3, "H"))

                if self.check_if_ship_fits(i, j, 2, 'H'):
                    action_list.append((i, j, 2, "H"))

            if self.hints[h][2] == "R":
                if self.check_if_ship_fits(i, j-3, 4, 'H'):
                    action_list.append((i, j-3, 4, "H"))

                if self.check_if_ship_fits(i, j-2, 3, 'H'):
                    action_list.append((i, j-2, 3, "H"))
                                                    
                if self.check_if_ship_fits(i, j-1, 2, 'H'):
                    action_list.append((i, j-1, 2, "H"))

            if self.hints[h][2] == "M":

                if j != 0 and j != 9:

                    if self.check_if_ship_fits(i, j-1, 4, 'H'):
                        action_list.append((i, j-1, 4, "H"))
                    if self.check_if_ship_fits(i, j-2, 4, 'H'):
                        action_list.append((i, j-2, 4, "H"))

                    if self.check_if_ship_fits(i, j-1, 3, 'H'):
                        action_list.append((i, j-1, 3, "H"))
                
                if i != 0 and i != 9:

                    if self.check_if_ship_fits(i-1, j, 4, 'V'):
                        action_list.append((i-1, j, 4, "V"))
                    if self.check_if_ship_fits(i-2, j, 4, 'V'):
                        action_list.append((i-2, j, 4, "V"))

                    if self.check_if_ship_fits(i-1, j, 3, 'V'):
                        action_list.append((i-1, j, 3, "V"))

        return action_list

    def print_board(self):
        """Imprime o tabuleiro."""

        for h in range(len(self.hints_final)):
            self.board[self.hints_final[h][0]][self.hints_final[h][1]] = self.hints_final[h][2]

        for i in range(10):
            for j in range(10):
                if self.board[i][j] == None:
                    print(".", end="")
                else:
                    print(self.board[i][j], end = "")
            print()

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.
        
        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """
        
        board = Board()

        for line in sys.stdin:
            line = line.strip().split("\t")
            if line[0] == "ROW":
                for i in range(len(line) - 1):
                    board.set_value(i, 10, int(line[i + 1]))
            elif line[0] == "COLUMN":
                for i in range(len(line) - 1):
                    board.set_value(10, i, int(line[i + 1]))
            elif line[0] == "HINT":
                if line[3] == "W":
                    board.set_value(int(line[1]), int(line[2]), "W")
                elif line[3] == "C":
                    board.set_boat((int(line[1]), int(line[2]), 1, "C"))
                    board.hints_final.append((int(line[1]), int(line[2]), "C"))
                else:
                    board.hints.append((int(line[1]), int(line[2]), line[3]))
                    board.hints_final.append((int(line[1]), int(line[2]), line[3]))

            else:
                continue
                
        return board

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = BimaruState(board)
        super().__init__(state)
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        
        board = state.board
        
        action_list = []
        
        action_list = board.place_ships_hints()
        if action_list == []:
            action_list = board.place_size_four_ship()
            if action_list == [] and board.boat_count[3] == 0:
                action_list = board.place_size_three_ship()
                if action_list == [] and board.boat_count[2] == 0:
                    action_list = board.place_size_two_ship()
                    if action_list == [] and board.boat_count[1] == 0:
                        action_list = board.place_size_one_ship()
        return action_list

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        new_board = state.board.copy_state()
        new_board.set_boat(action)
        for i in range(len(new_board.hints)):
            if new_board.hints[i][0] == action[0] and new_board.hints[i][1] == action[1]:
                new_board.hints.pop(i)
                break
        return BimaruState(new_board)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        board = state.board
        if board.boat_count.count(0) != 4:
            return False
        
        for i in range(10):
            if board.get_number_of_cells_left_col(i) != 0 or board.get_number_of_cells_left_row(i) != 0:
                return False

        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        pass


if __name__ == "__main__":
    
    # Ler o ficheiro do standard input
    board = Board.parse_instance()
    
    # Usar uma técnica de procura para resolver a instância
    bimaru = Bimaru(board)
    instrumented = InstrumentedProblem(bimaru)
    
    # Retirar a solução a partir do nó resultante
    goal_node = depth_first_tree_search(instrumented)
    
    # Imprimir para o standard output no formato indicado
    goal_node.state.board.print_board()
