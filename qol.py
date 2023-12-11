def draw_text(win, font, text, pos: tuple, colour=(255, 255, 255)):
    win.blit(font.render(text, 0, colour), pos)

def clamp(val, min_val, max_val):
    if val < min_val:
        return min_val
    elif val > max_val:
        return max_val
    return val
