from menu import menu
from game import game
import screen

if __name__ == '__main__':
    screen.init()

    run = 1
    while run:
        seed, close_ = menu()
        if close_:
            run = 0
        else:
            game(seed)

    screen.quit()
