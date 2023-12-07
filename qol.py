def draw_text(win, font, text, x, y, colour=(255, 255, 255)):
    win.blit(font.render(text, 0, colour), (x, y))

def clamp(val, min_val, max_val):
    if val < min_val:
        return min_val
    elif val > max_val:
        return max_val
    return val
