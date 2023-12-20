from menu import menu
from game import game
import screen

if __name__ == '__main__':
    screen.init()

    run = 1
    while run:
        if menu():
            run = 0
        else:
            game()

    screen.quit()
