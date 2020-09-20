import hashlib
import socket
import time
import pygame

pygame.init()


def main():
    class Button:
        def __init__(self, color_button, color_text, position_button, text=None, size_police=0):
            self.color_button = color_button
            self.text = text
            if self.text is not None:
                self.font_ = pygame.font.SysFont("arial", size_police * height // 1080)
                self.color_text = color_text
                self.position_button = [position_button[0] - self.font_.size(self.text)[0] // 2 - 5,
                                        position_button[1] - self.font_.size(self.text)[1] // 2,
                                        self.font_.size(self.text)[0] + 10,
                                        self.font_.size(self.text)[1]]
            else:
                self.position_button = position_button

        def display_button(self):
            if self.text is not None:
                pygame.draw.rect(Screen, self.color_button,
                                 [self.position_button[0], self.position_button[1], self.position_button[2],
                                  self.position_button[3]])
                Screen.blit(self.font_.render(self.text, False, self.color_text), self.pos_text())
            else:
                pygame.draw.line(Screen, (255, 0, 0), (self.position_button[0],
                                                       self.position_button[1]),
                                 (self.position_button[0] + self.position_button[2],
                                  self.position_button[1] + self.position_button[3]), 5)
                pygame.draw.line(Screen, (255, 0, 0), (self.position_button[0],
                                                       self.position_button[1] + self.position_button[3]),
                                 (self.position_button[0] + self.position_button[2],
                                  self.position_button[1]), 5)
                pygame.draw.rect(Screen, (255, 255, 255), [0, 0, height // 20 + 3, height // 20 + 3], 3)

        def button_clicked(self):
            x, y = pos
            if self.position_button[0] + self.position_button[2] >= x >= self.position_button[0] and \
                    self.position_button[1] + self.position_button[3] >= y >= self.position_button[1]:
                return True
            return False

        def pos_text(self):
            return self.position_button[0] + (self.position_button[2] - self.font_.size(self.text)[0]) // 2, \
                   self.position_button[1] + (self.position_button[3] - self.font_.size(self.text)[1]) // 2

    def display_session():
        if len(sessions) > scroll:
            button_session_1 = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height * 4 // 10],
                                      sessions[0 + scroll], 50)
            list_button.append(button_session_1)
        if len(sessions) > 1 + scroll:
            button_session_2 = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height * 5 // 10],
                                      sessions[1 + scroll], 50)
            list_button.append(button_session_2)
        if len(sessions) > 2 + scroll:
            button_session_3 = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height * 6 // 10],
                                      sessions[2 + scroll], 50)
            list_button.append(button_session_3)
        if len(sessions) > 3 + scroll:
            button_session_4 = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height * 7 // 10],
                                      sessions[3 + scroll], 50)
            list_button.append(button_session_4)
        if len(sessions) > 4 + scroll:
            button_session_5 = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height * 8 // 10],
                                      sessions[4 + scroll], 50)
            list_button.append(button_session_5)
        scroll_up.display_button()
        scroll_down.display_button()

    def update_info():
        client.send("|getsessions".encode('utf-8'))
        reponse_ = client.recv(1023).decode('utf-8')
        sessions_ = reponse_[1:].split('|')
        if sessions_ == [""]:
            sessions_ = []
        client.send("|getsession".encode('utf-8'))
        session_ = client.recv(1023).decode('utf-8')
        if session_ == '|':
            session_ = None
        if session is None:
            message_ = None
        else:
            client.send('|getchat'.encode('utf-8'))
            reponse_ = client.recv(1023).decode('utf-8').split('|')
            message_ = []
            for text in range(len(reponse_) // 2):
                message_.append([reponse_[text * 2], reponse_[text * 2 + 1]])
        return session_, sessions_, message_
    sessions = []
    scroll = 0
    size_screen = pygame.display.Info()
    running = True
    height = size_screen.current_h
    width = size_screen.current_w
    input_value = ""
    input_ = None
    user_input = ""
    password_input = ""
    pressed = {}
    message = None
    menu = 'start'
    list_button = []
    button_connection = Button((127, 127, 127), (255, 255, 255), [width // 2, height * 5 // 12], "Connexion", 50)
    button_new_client = Button((127, 127, 127), (255, 255, 255), [width // 2, height * 7 // 12], "Nouveau membre", 50)
    button_user = Button((255, 255, 255), (0, 0, 0), [width // 2, height * 5 // 12], "Identifiant", 30)
    button_password = Button((255, 255, 255), (0, 0, 0), [width // 2, height // 2], "Mot de passe", 30)
    button_quit = Button((0, 0, 0), None, [0, 0, height // 20, height // 20])
    button_submit = Button((127, 127, 127), (255, 255, 255), [width // 2, height * 2 // 3], 'Valider', 50)
    button_new_session = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height // 10], 'Nouvelle session',
                                40)
    session = None
    button_session = Button((127, 127, 127), (255, 255, 255), [width * 7 // 8, height // 5], 'connexion session', 40)
    scroll_up = Button((127, 127, 127), (255, 255, 255), [width * 15 // 16, height * 3 // 10], '↑', 40)
    scroll_down = Button((127, 127, 127), (255, 255, 255), [width * 15 // 16, height * 9 // 10], '↓', 40)
    pos = (0, 0)
    font_size = 50 * height // 1080
    big_font = pygame.font.SysFont("arial", font_size)
    small_font = pygame.font.SysFont("arial", font_size // 2)
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.FULLSCREEN)
    Screen = screen.copy()
    r_time = time.time() - 5
    touche = time.time() - 5
    while running:
        onclick = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pressed[event.key] = True
                if event.key not in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE, pygame.K_TAB):
                    try:
                        if not (input_ == 'user' and (event.unicode == ' ' or len(input_value) >= 16)) and \
                                event.unicode not in ['\\', '|']:
                            input_value += event.unicode
                    except ValueError:
                        pass
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                    if input_ == "user":
                        user_input = input_value
                        input_ = "password"
                    elif input_ == "password":
                        password_input = input_value
                        input_ = None
                    else:
                        input_ = "entrer"
                    input_value = ""
            elif event.type == pygame.KEYUP:
                pressed[event.key] = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                onclick = True
                pos = pygame.mouse.get_pos()
        pygame.draw.rect(Screen, (0, 0, 0), [0, 0, width, height])
        pygame.draw.rect(Screen, (255, 255, 255), [0, 0, width, height], 5)
        pygame.draw.line(Screen, (255, 255, 255), (0, height * 94 // 100), (width, height * 94 // 100))
        list_button = []
        Screen.blit(big_font.render('Quitter : ECHAP', False, (255, 255, 255)), (5, height * 94 // 100))
        if pressed.get(pygame.K_ESCAPE) or (onclick and button_quit.button_clicked()):
            running = False
            continue
        if time.time() > touche + 0.1 and pressed.get(pygame.K_BACKSPACE) and input_ is not None:
            touche = time.time() + 0.05
            input_value = input_value[:-1]
        if menu == 'start':
            pygame.draw.rect(Screen, (255, 255, 255), [width // 4, height // 4, width // 2, height // 2], 5)
            button_connection.display_button()
            button_new_client.display_button()
            if onclick:
                if button_connection.button_clicked():
                    menu = 'connexion'
                elif button_new_client.button_clicked():
                    menu = 'new client'
        elif menu == 'main' or menu == 'new session' or menu == 'session':
            if time.time() > r_time + 4:
                session, sessions, message = update_info()
                r_time = time.time()
            if session is not None:
                pass  # affichage chat + barre envoie msg
            pygame.draw.line(Screen, (255, 255, 255), (width * 3 // 4, 0), (width * 3 // 4, height * 94 // 100), 1)
            button_new_session.display_button()
            button_session.display_button()
            scroll_up.display_button()
            scroll_down.display_button()
            display_session()
            button_quit.display_button()
            for i in range(len(list_button)):
                if onclick and list_button[i].button_clicked():
                    client.send("|session|{}".format(sessions[i + scroll]).encode('utf-8'))
                    if client.recv(1023).decode('utf-8') == '1':
                        pass
                    session, sessions, message = update_info()
                list_button[i].display_button()

            if onclick:
                if len(sessions) > 5:
                    if scroll_up.button_clicked():
                        scroll -= 1
                        scroll %= len(sessions)
                        if scroll > len(sessions) - 5:
                            scroll = len(sessions) - 5
                    elif scroll_down.button_clicked():
                        scroll += 1
                        scroll %= len(sessions)
                        if scroll > len(sessions) - 5:
                            scroll = 0
                if button_new_session.button_clicked():
                    menu = 'new session'
                elif button_session.button_clicked():
                    menu = 'session'
        if menu == 'connexion' or menu == 'new client' or menu == 'new session' or menu == 'session':
            pygame.draw.rect(Screen, (255, 255, 255), [width // 4, height // 4, width // 2, height // 2], 5)
            button_submit.display_button()
            if input_ == "user":
                pygame.draw.rect(Screen, (255, 255, 255),
                                 [width * 5 // 12, height * 5 // 12 - 15, width // 6, height // 30],
                                 2)
                Screen.blit(small_font.render(input_value, False, (255, 255, 255)),
                            (width * 5 // 12 + 5, height * 5 // 12 - 15))
            else:
                Button((255, 255, 255), (0, 0, 0), [width // 2, height * 5 // 12],
                       "Identifiant" if user_input == "" else user_input, 30).display_button()
            if input_ == "password":
                pygame.draw.rect(Screen, (255, 255, 255),
                                 [width * 5 // 12, height // 2 - 15, width // 6, height // 30], 2)
                Screen.blit(small_font.render(input_value, False, (255, 255, 255)),
                            (width * 5 // 12 + 5, height // 2 - 15))
            else:
                Button((255, 255, 255), (0, 0, 0), [width // 2, height // 2],
                       "Mot de passe" if password_input == "" else password_input, 30).display_button()
            if onclick or input_ == 'entrer':
                if button_user.button_clicked() and input_ is None:
                    input_ = "user"
                    input_value = user_input
                elif button_password.button_clicked() and input_ is None:
                    input_ = "password"
                    input_value = password_input
                elif input_ == "user" and not (width * 5 // 12 < pos[0] < width * 7 // 12 and height // 2 < pos[1]
                                               < height // 2 + height // 30):
                    input_ = None
                    user_input = input_value
                    input_value = ""
                elif input_ == "password" and not (
                        width * 5 // 12 < pos[0] < width * 7 // 12 and height * 7 // 12 < pos[1] < height * 7 // 12 +
                        height // 30):
                    input_ = None
                    password_input = input_value
                    input_value = ""
                if (button_submit.button_clicked() or input_ == 'entrer') and user_input != '' and password_input != '':
                    mdp = hashlib.md5(password_input.encode('utf-8')).hexdigest()
                    if menu == 'connexion':
                        message = "|login|" + user_input + "|" + mdp
                    elif menu == 'new client':
                        message = "|newlogin|" + user_input + "|" + mdp
                    elif menu == "new session":
                        message = "|newsession|" + user_input + "|" + mdp
                    elif menu == "session":
                        message = "|session|" + user_input + "|" + mdp
                    client.send(message.encode("utf-8"))
                    reponse = client.recv(1023).decode('utf-8')
                    if reponse == '1':
                        menu = 'main'
                        session, sessions, message = update_info()
                    user_input, password_input = '', ''
                if input_ == 'entrer':
                    input_ = None
        screen.blit(pygame.transform.scale(Screen, (width, height)), (0, 0))
        # screen.blit(pygame.transform.scale(Screen, (width * 4 // 5, height * 4 // 5)), (width // 10, height // 10))
        pygame.display.flip()
    client.close()
    pygame.quit()


adresseIP = "86.210.7.140"  # Ici, le poste local
port = 12800  # Se connecter sur le port 50000

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((adresseIP, port))
    main()
    print("Connexion fermée")
except ConnectionRefusedError:
    print("erreur de connexion")
