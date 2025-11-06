import pygame as pg
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_RETURN, K_BACKSPACE

# ---------------------------- Config ----------------------------
WIDTH, HEIGHT = 600, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LINE = (10, 10, 10)
RED = (220, 40, 40)
GRAY = (200, 200, 200)
DGRAY = (60, 60, 60)
BLUE = (40, 120, 220)

HEADER_H = 72    # top header band (roles + turn)

# ---------------------------- Globals ---------------------------
XO = 'x'
winner = None
draw = False
TTT = [[None] * 3, [None] * 3, [None] * 3]
mode = None        # "PVP" or "PVC"
p1_name = "Player 1"   # X
p2_name = "Player 2"   # O or "Computer"
finish_snapshot = None # final frame (board + red line) 
win_line = None        # Stores line coordinates

# ---------------------------- Pygame init -----------------------
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT), 0, 32)
pg.scrap.init() 
pg.mouse.set_visible(True) 
pg.display.set_caption("Tic Tac Toe By Azhar")
CLOCK = pg.time.Clock()

# ---------------------------- Assets ----------------------------
try:
    opening = pg.image.load('tic tac opening.png')
except:
    opening = pg.Surface((WIDTH, HEIGHT))
    opening.fill((30, 30, 30))
opening = pg.transform.scale(opening, (WIDTH, HEIGHT))

cell_size = int((HEIGHT - HEADER_H) / 3) - 40
try:
    x_img = pg.image.load('x.png'); o_img = pg.image.load('o.png')
    x_img = pg.transform.scale(x_img, (cell_size, cell_size))
    o_img = pg.transform.scale(o_img, (cell_size, cell_size))
except:
    x_img = pg.Surface((cell_size, cell_size), pg.SRCALPHA)
    o_img = pg.Surface((cell_size, cell_size), pg.SRCALPHA)
    ftmp = pg.font.Font(None, int(cell_size * 0.9))
    xt = ftmp.render("X", True, (250, 30, 30))
    ot = ftmp.render("O", True, (30, 150, 250))
    x_img.blit(xt, xt.get_rect(center=(cell_size//2, cell_size//2)))
    o_img.blit(ot, ot.get_rect(center=(cell_size//2, cell_size//2)))

font_title = pg.font.Font(None, 44)
font_large = pg.font.Font(None, 56)
font_med = pg.font.Font(None, 36)
font_small = pg.font.Font(None, 26)

# ---------------------------- UI Helpers ------------------------
class Button:
    def __init__(self, rect, label, bg=DGRAY, fg=WHITE, hover=BLUE, font=font_med):
        self.rect = pg.Rect(rect); self.label = label
        self.bg = bg; self.fg = fg; self.hover = hover; self.font = font
    def draw(self, surf):
        is_hover = self.rect.collidepoint(pg.mouse.get_pos())
        pg.draw.rect(surf, self.hover if is_hover else self.bg, self.rect, border_radius=10)
        text = self.font.render(self.label, True, self.fg)
        surf.blit(text, text.get_rect(center=self.rect.center))
    def clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# ---------------------------- Board & Status --------------------
def draw_board():
    screen.fill(WHITE)
    pg.draw.line(screen, LINE, (int(WIDTH/3), HEADER_H), (int(WIDTH/3), HEIGHT), 7)
    pg.draw.line(screen, LINE, (int(WIDTH*2/3), HEADER_H), (int(WIDTH*2/3), HEIGHT), 7)
    y1 = HEADER_H + int((HEIGHT-HEADER_H)/3); y2 = HEADER_H + int(2*(HEIGHT-HEADER_H)/3)
    pg.draw.line(screen, LINE, (0, y1), (WIDTH, y1), 7)
    pg.draw.line(screen, LINE, (0, y2), (WIDTH, y2), 7)

def draw_status():
    pg.draw.rect(screen, WHITE, (0, 0, WIDTH, HEADER_H))
    roles = f"X: {p1_name}     •     O: {p2_name}"
    if winner is None and not draw:
        msg, color = f"{XO.upper()}'s Turn", BLUE
    elif winner is not None:
        msg, color = f"{(p1_name if winner=='x' else p2_name)} won!", RED
    else:
        msg, color = "Game Draw!", RED
    screen.blit(font_med.render(roles, True, BLACK), (WIDTH//2 - font_med.size(roles)[0]//2, 12))
    screen.blit(font_small.render(msg, True, color), (WIDTH//2 - font_small.size(msg)[0]//2, 44))

# ---------------------------- Win/Draw --------------------------
def check_win():
    global TTT, winner, draw, win_line
    cell_h = (HEIGHT - HEADER_H) / 3
    
    # 1. Check rows
    for r in range(3):
        if (TTT[r][0] == TTT[r][1] == TTT[r][2]) and (TTT[r][0] is not None):
            winner = TTT[r][0]
            y = int(HEADER_H + (r + 0.5) * cell_h)
            win_line = ((20, y), (WIDTH - 20, y))
            return
    # 2. Check cols
    for c in range(3):
        if (TTT[0][c] == TTT[1][c] == TTT[2][c]) and (TTT[0][c] is not None):
            winner = TTT[0][c]
            x = int((c + 0.5) * (WIDTH / 3))
            win_line = ((x, HEADER_H + 20), (x, HEIGHT - 20))
            return
    # 3. Check diagonals
    if (TTT[0][0] == TTT[1][1] == TTT[2][2]) and (TTT[0][0] is not None):
        winner = TTT[0][0]
        win_line = ((20, HEADER_H + 20), (WIDTH - 20, HEIGHT - 20))
        return
    if (TTT[0][2] == TTT[1][1] == TTT[2][0]) and (TTT[0][2] is not None):
        winner = TTT[0][2]
        win_line = ((WIDTH - 20, HEADER_H + 20), (20, HEIGHT - 20))
        return
    
    # 4. Check draw
    if all(all(cell is not None for cell in row) for row in TTT):
        draw = True

# ---------------------------- drawXO ----------------------------
def drawXO(row, col):
    global TTT, XO
    # This function only updates the TTT data model
    TTT[row - 1][col - 1] = XO
    if XO == 'x':
        XO = 'o'
    else:
        XO = 'x'

# ---------------------------- Moves (click handler) -------------
def user_click():
    x, y = pg.mouse.get_pos()
    if y < HEADER_H: return
    # columns
    if x < WIDTH/3: col = 1
    elif x < WIDTH*2/3: col = 2
    elif x < WIDTH: col = 3
    else: col = None
    # rows
    gy = y - HEADER_H
    cell_h = (HEIGHT - HEADER_H) / 3
    if gy < 0: return
    if gy < cell_h: row = 1
    elif gy < 2*cell_h: row = 2
    elif gy < 3*cell_h: row = 3
    else: row = None

    if row and col and TTT[row-1][col-1] is None and winner is None:
        drawXO(row, col)
        check_win()

# ---------------------------- Minimax AI (O) --------------------
def empty_cells(state): return [(r, c) for r in range(3) for c in range(3) if state[r][c] is None]
def evaluate_state(state):
    lines = [[(0,0),(0,1),(0,2)],[(1,0),(1,1),(1,2)],[(2,0),(2,1),(2,2)],
             [(0,0),(1,0),(2,0)],[(0,1),(1,1),(2,1)],[(0,2),(1,2),(2,2)],
             [(0,0),(1,1),(2,2)],[(0,2),(1,1),(2,0)]]
    for a,b,c in lines:
        v1,v2,v3 = state[a[0]][a[1]], state[b[0]][b[1]], state[c[0]][c[1]]
        if v1 is not None and v1 == v2 == v3: return 1 if v1 == 'o' else -1
    if any(None in row for row in state): return None
    return 0
def minimax(state, maximizing):
    score = evaluate_state(state)
    if score is not None: return score, None
    best_move = None
    if maximizing:  # 'o'
        best = -999
        for r,c in empty_cells(state):
            state[r][c] = 'o'; val,_ = minimax(state, False); state[r][c] = None
            if val > best: best, best_move = val, (r,c)
        return best, best_move
    else:           # 'x'
        best = 999
        for r,c in empty_cells(state):
            state[r][c] = 'x'; val,_ = minimax(state, True); state[r][c] = None
            if val < best: best, best_move = val, (r,c)
        return best, best_move
def ai_move_if_needed():
    global XO
    if mode != "PVC" or winner or draw or XO != 'o': return
    _, move = minimax(TTT, True)
    if move:
        r,c = move
        drawXO(r+1, c+1)
        check_win()

# ---------------------------- Screens --------------------------
def title_menu():
    screen.blit(opening, (0, 0))
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA); overlay.fill((0,0,0,130))
    screen.blit(overlay, (0, 0))
    top = font_small.render("TIC TAC TOE GAME Player Vs Player and Player VS Computer by Azhar", True, WHITE)
    title = font_large.render("Menu", True, WHITE)
    btn_w, btn_h, gap, start_y = 260, 54, 18, 150
    b_pvp = Button((WIDTH//2 - btn_w//2, start_y, btn_w, btn_h), "Player Vs Player")
    b_pvc = Button((WIDTH//2 - btn_w//2, start_y + btn_h + gap, btn_w, btn_h), "Player Vs Computer")
    b_exit= Button((WIDTH//2 - btn_w//2, start_y + 2*(btn_h + gap), btn_w, btn_h), "Exit", bg=BLACK)
    while True:
        for event in pg.event.get():
            if event.type == QUIT: pg.quit(); sys.exit()
            if b_pvp.clicked(event): return "PVP"
            if b_pvc.clicked(event): return "PVC"
            if b_exit.clicked(event): pg.quit(); sys.exit()
        screen.blit(opening, (0, 0)); screen.blit(overlay, (0, 0))
        screen.blit(top, top.get_rect(center=(WIDTH//2, 60)))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
        b_pvp.draw(screen); b_pvc.draw(screen); b_exit.draw(screen)
        pg.display.update(); CLOCK.tick(FPS)

def text_input_screen(prompt):
    text_value = ""; input_rect = pg.Rect(WIDTH//2 - 140, HEIGHT//2 - 25, 280, 50)
    all_selected = False # New state to track 'Select All'
    
    while True:
        for event in pg.event.get():
            if event.type == QUIT: pg.quit(); sys.exit()
            if event.type == KEYDOWN:
                # Check for modifier keys (Ctrl)
                mods = pg.key.get_mods()
                if mods & pg.KMOD_CTRL:
                    if event.key == pg.K_v: # PASTE (Ctrl+V)
                        try:
                            clipboard_text = pg.scrap.get(pg.SCRAP_TEXT)
                            if clipboard_text:
                                # Decode bytes from clipboard and remove null chars
                                paste_text = clipboard_text.decode('utf-8').replace('\x00', '')
                                if all_selected:
                                    text_value = paste_text
                                    all_selected = False
                                else:
                                    text_value += paste_text
                                text_value = text_value[:20] # Enforce max length
                        except Exception as e:
                            print(f"Clipboard paste error (this is common): {e}")

                    elif event.key == pg.K_a: # SELECT ALL (Ctrl+A)
                        all_selected = True

                    elif event.key == pg.K_c: # COPY (Ctrl+C)
                        if all_selected:
                            try:
                                pg.scrap.put(pg.SCRAP_TEXT, text_value.encode('utf-8'))
                            except Exception as e:
                                print(f"Clipboard copy error: {e}")

                    elif event.key == pg.K_x: # CUT (Ctrl+X)
                        if all_selected:
                            try:
                                pg.scrap.put(pg.SCRAP_TEXT, text_value.encode('utf-8'))
                                text_value = ""
                                all_selected = False
                            except Exception as e:
                                print(f"Clipboard cut error: {e}")
                
                # --- Original key handling ---
                elif event.key == K_RETURN and text_value.strip():
                    return text_value.strip()
                
                elif event.key == K_BACKSPACE:
                    if all_selected:
                        text_value = ""
                        all_selected = False
                    else:
                        text_value = text_value[:-1]
                
                else: # Regular character input
                    if len(text_value) < 20 and 32 <= event.key <= 126:
                        if all_selected:
                            text_value = event.unicode # Replace selected text
                            all_selected = False
                        else:
                            text_value += event.unicode # Add to text
            
            # If user clicks off the "selection"
            elif event.type == MOUSEBUTTONDOWN and not input_rect.collidepoint(event.pos):
                all_selected = False

        screen.fill((30,30,30))
        screen.blit(font_med.render(prompt, True, WHITE), (WIDTH//2 - font_med.size(prompt)[0]//2, HEIGHT//2 - 60))

        # --- Visual feedback for selection ---
        bg_color, text_color, border_color = WHITE, BLACK, BLUE
        if all_selected:
            bg_color, text_color, border_color = BLUE, WHITE, WHITE # Invert colors when selected
            
        pg.draw.rect(screen, bg_color, input_rect, border_radius=6)
        pg.draw.rect(screen, border_color, input_rect, 2, border_radius=6)
        
        typed = font_med.render(text_value, True, text_color)
        screen.blit(typed, typed.get_rect(midleft=(input_rect.x + 10, input_rect.centery)))
        
        hint = font_small.render("Press Enter to confirm (Ctrl+V/C/X enabled)", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
        
        pg.display.update(); CLOCK.tick(FPS)

def collect_names(selected_mode):
    global p1_name, p2_name
    if selected_mode == "PVP":
        p1_name = text_input_screen("Enter Player 1 name (X):")
        p2_name = text_input_screen("Enter Player 2 name (O):")
    else:
        p1_name = text_input_screen("Enter Player name (X):")
        p2_name = "Computer"

def announce_roles_then_start():
    render_all() # Use render_all to draw board and status
    msg = font_title.render("Get Ready!", True, BLACK)
    screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEADER_H + 40)))
    r1 = font_med.render(f"{p1_name} is X", True, BLACK)
    r2 = font_med.render(f"{p2_name} is O", True, BLACK)
    screen.blit(r1, r1.get_rect(center=(WIDTH//2, HEADER_H + 85)))
    screen.blit(r2, r2.get_rect(center=(WIDTH//2, HEADER_H + 120)))
    pg.display.update(); pg.time.delay(900)

def result_menu_overlay(snapshot): # <-- MODIFICATION 1: Accept snapshot
    btn_w, btn_h, gap = 220, 48, 14
    start_y = HEIGHT//2 - 10
    b_again = Button((WIDTH//2 - btn_w//2, start_y, btn_w, btn_h), "Play Again")
    b_menu  = Button((WIDTH//2 - btn_w//2, start_y + btn_h + gap, btn_w, btn_h), "Return to Menu")
    b_exit  = Button((WIDTH//2 - btn_w//2, start_y + 2*(btn_h + gap), btn_w, btn_h), "Exit", bg=BLACK)
    outcome = f"{(p1_name if winner=='x' else p2_name)} wins!" if winner else "Game Draw!"
    
    dim = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA); dim.fill((0,0,0,140))
    
    while True:
        for event in pg.event.get():
            if event.type == QUIT: pg.quit(); sys.exit()
            if b_again.clicked(event): return "AGAIN"
            if b_menu.clicked(event):  return "MENU"
            if b_exit.clicked(event):  pg.quit(); sys.exit()
        
        # MODIFICATION 2: Draw the snapshot FIRST, every frame
        screen.blit(snapshot, (0, 0)) 
        
        # Now draw the dimming layer and menu on top
        screen.blit(dim, (0, 0))
        banner = font_large.render(outcome, True, WHITE)
        screen.blit(banner, banner.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
        b_again.draw(screen); b_menu.draw(screen); b_exit.draw(screen)
        
        pg.display.update(); CLOCK.tick(FPS)

# ---------------------------- Flow ------------------------------
def reset_board():
    global TTT, XO, winner, draw, finish_snapshot, win_line
    XO = 'x'; winner = None; draw = False; finish_snapshot = None; win_line = None
    TTT = [[None] * 3, [None] * 3, [None] * 3]

def render_all():
    draw_board(); draw_status()
    margin = 30; cell_w = WIDTH/3; cell_h = (HEIGHT - HEADER_H)/3
    for r in range(3):
        for c in range(3):
            v = TTT[r][c]
            if v:
                posx = int(c * cell_w + margin)
                posy = int(HEADER_H + r * cell_h + margin)
                screen.blit(x_img if v == 'x' else o_img, (posx, posy))
                
    # Draw win line here if a winner exists
    if win_line:
        pg.draw.line(screen, RED, win_line[0], win_line[1], 7)

def game_loop():
    global finish_snapshot
    reset_board(); announce_roles_then_start()
    while True:
        for event in pg.event.get():
            if event.type == QUIT: pg.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if winner is None and not draw:
                    user_click()
                    if mode == "PVC": ai_move_if_needed()

        if winner is None and not draw:
            render_all()
        else:
            # Game is finished (winner or draw)
            if finish_snapshot is None:
                # 1. Ensure everything is drawn (including the final mark and red line)
                render_all() 
                # 2. Take the snapshot
                pg.display.update()
                finish_snapshot = screen.copy()

            # MODIFICATION 3: Pass the snapshot to the menu function
            choice = result_menu_overlay(finish_snapshot) 
            
            if choice == "AGAIN":
                reset_board(); announce_roles_then_start()
            elif choice == "MENU":
                return

        pg.display.update(); CLOCK.tick(FPS)

def main():
    global mode
    while True:
        mode = title_menu()
        collect_names(mode)
        game_loop()

if __name__ == "__main__":
    main()