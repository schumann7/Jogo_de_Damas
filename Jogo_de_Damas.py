import pygame
import sys
 
# Defina as constantes
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
 
# Defina as cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (153,153,255)
GREY = (128, 128, 128)

CROWN = pygame.transform.scale(pygame.image.load('coroa.png'), (88, 60))

# Classe para representar as peças
class Piece:
    PADDING = 8 #Distância da peça e da borda das casas do tabuleiro
    OUTLINE = 4 #Tamanho do contorno

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False 

        self.x = 0
        self.y = 0
        self.calc_pos()

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos() #Chama o método de calculo da posição da peça

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING # Define o raio da peça como o tamanho de um quadrado menos o valor de padding
        pygame.draw.circle(win, GREY, (self.x, self.y),(radius + self.OUTLINE)) # Desenha um circulo grande para servir de borda
        pygame.draw.circle(win, self.color, (self.x, self.y),(radius)) #Desenha um circulo menor
        
        if self.king: # Verifica se a peça é rei
            win.blit(CROWN, (self.x- CROWN.get_width()//2, self.y - CROWN.get_height()//2)) # Centraliza a coroa e a posiciona na peça

    def calc_pos(self): # Calcula a posição x e y dependendo da coluna e fileira que a peça está
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2 # Divide o valor por 2 para conseguir o centro da posição
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2 # Divide o valor por 2 para conseguir o centro da posição

# Classe para representar o tabuleiro
class Board:
    def __init__(self):
        self.board = []

        self.blue_left = self.white_left = 12 # Define quantas peças ainda restam, começando em 12
        self.blue_kings = self.white_kings = 0 # Define quantas peças viraram reis, começando em 0

        self.create_pieces()

    def create_pieces(self): 
        for row in range(ROWS):
            self.board.append([]) # Adiciona lista vazia no tabuleiro
            for col in range(COLS):
                if col % 2 == ((row +1) % 2): # if para adicionar peças alternando as casas
                    if row < 3: # Só desenhar nas 3 primeiras fileiras
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, BLUE))
                    else:
                        self.board[row].append(0) # Se não tiver peça o valor é zero
                else:
                    self.board[row].append(0) # Se não tiver peça o valor é zero

    def draw_squares(self, win):
        win.fill(BLACK) # Preenche a janela com a cor preta
        for row in range(ROWS): # Passa por todas as fileiras do tabuleiro
            for col in range(row % 2, COLS, 2): # Pula casas de 2 em 2
                pygame.draw.rect(win, LIGHTBLUE, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)) #Desenha o quadrado vermelho
    
    def draw_pieces(self, win): # Criado por mim, alterar dps
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0: # Se tiver peça
                    piece.draw(win) # Desenhar peça

    def get_valid_moves(self, piece):
        moves={}
        left = piece.col - 1
        right = piece.col +1
        row = piece.row

        if piece.color == BLUE or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))

        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
           
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)

                    moves.update(self._traverse_left(r+step, row, step, color, left-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1, skipped=last))
                break

            elif current.color == color:
                break
            else:
                last = [current]

            left -=1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)

                    moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=last))
                break

            elif current.color == color:
                break
            else:
                last = [current]

            right +=1

        return moves
    
    def select(self, row, col):
        return self.board[row][col]
 
    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS -1 or row == 0: # Verifica se a posição faz a peça virar rei
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings +=1
            else:
                self.blue_kings +=1
 
    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.color == BLUE:
                self.blue_left -=1
            else:
                self.white_left -=1
        
    def is_winner(self, color):
        if color == BLUE:
            if self.blue_left == 0:
                return True
        else:
            if self.white_left == 0:
                return True

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
    
    def update(self):
        self.board.draw_pieces(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

        if self.board.is_winner(BLUE) == True: # Verifica se vermelho venceu
            pygame.quit() 
            sys.exit()

        if self.board.is_winner(WHITE) == True: # Verifica se branco venceu
            pygame.quit() 
            sys.exit()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = BLUE
        self.valid_moves = {}

    def reset(self):
        self._init()
    
    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
       
        piece = self.board.select(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        
        return False

    def _move(self, row, col):
        piece = self.board.select(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True
    
    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, RED, (col*SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)
    
    def change_turn(self):
        self.valid_moves = {}
        if self.turn == BLUE:
            self.turn = WHITE
        else:
            self.turn = BLUE

# Detectar em qual casa ocorre o clique do mouse
def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x //SQUARE_SIZE
    return row, col

# Função principal
def main():
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Cria janela
    pygame.display.set_caption("Jogo de Damas") # Define nome da janela
 
    game = Game(WIN)
     
    selected_piece = None

    run = True # Evento de loop
    while run:
        for event in pygame.event.get(): # Evento de loop que verifica ocorrência de eventos
            if event.type == pygame.QUIT: # Se evento for sair do jogo, para o loop
                run = False
 
            if event.type == pygame.MOUSEBUTTONDOWN: # Verifica o clique do mouse
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if game.turn == BLUE:
                    game.select(row, col)
                elif game.turn == WHITE:
                    game.select(row, col)
            
        game.update()
 
    pygame.quit() #Fim do loop, fecha o jogo
    sys.exit()
 
if __name__ == "__main__":
    main()