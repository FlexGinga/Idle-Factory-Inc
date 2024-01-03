import pygame

def draw_text(win: pygame.Surface, font: pygame.font.Font, text, pos: tuple, colour=(255, 255, 255),
              center_x: bool = False, center_y: bool = False, max_length: int = 0):
    text_surfs = []
    if type(text) == str:
        text_surfs.append(font.render(text, 0, colour))
    elif type(text) in [list, tuple]:
        adjusted_text = []
        for line in text:
            if 0 < max_length < len(line):

                to_add = line
                splittable = True
                while len(to_add) > max_length and splittable:
                    split = None
                    for i in range(max_length):
                        if to_add[i] == " ":
                            split = i
                    if split is None:
                        splittable = False
                    else:
                        adjusted_text.append(to_add[:split])
                        to_add = to_add[split+1:]
                adjusted_text.append(to_add)

            else:
                adjusted_text.append(line)

        for line in adjusted_text:
            text_surfs.append(font.render(line, 0, colour))
    else:
        raise Exception("type error")

    line_height = text_surfs[0].get_height() + 4
    half_height = line_height * len(text_surfs) // 2
    for index, text_surf in enumerate(text_surfs):
        x_offset, y_offset = 0, 0
        if center_x:
            x_offset = text_surf.get_width() // 2
        if center_y:
            y_offset = text_surf.get_height() // 2

        draw_pos = pos[0] - x_offset, pos[1] - y_offset - half_height + line_height * (index + 0.5)

        win.blit(text_surf, draw_pos)


def clamp(val, min_val, max_val):
    if val < min_val:
        return min_val
    elif val > max_val:
        return max_val
    return val


def seconds_to_time(seconds: int):
    str_hours = int(seconds // 3600 % 24)
    if str_hours < 10:
        str_hours = f"0{str_hours}"
    else:
        str_hours = str(str_hours)

    str_minutes = int(seconds // 60 % 60)
    if str_minutes < 10:
        str_minutes = f"0{str_minutes}"
    else:
        str_minutes = str(str_minutes)

    str_seconds = int(seconds % 60)
    if str_seconds < 10:
        str_seconds = f"0{str_seconds}"
    else:
        str_seconds = str(str_seconds)

    time = str_hours + ":" + str_minutes + ":" + str_seconds
    return time
