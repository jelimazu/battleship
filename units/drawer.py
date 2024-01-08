from io import BytesIO

import PIL.Image
import asyncio

background = PIL.Image.open('img/clear_field.png')
selected_box = PIL.Image.open('img/selected_box.png')
hit = PIL.Image.open('img/hit.png')
miss = PIL.Image.open('img/miss.png')
destroy = PIL.Image.open('img/destroy.png')


async def draw_field(field):
    img_field = background.copy()
    for i in range(6):
        for j in range(6):
            if field[i][j] == '1' or field[i][j] == '2' or field[i][j] == '3' or field[i][j] == '4' or field[i][j] == '5' or field[i][j] == '6':
                img_field.paste(selected_box.convert('RGB'), (50 + j * 100 - 5 * j, 50 + i * 100 - 5 * i), selected_box)
            if field[i][j] == '5':
                img_field.paste(hit.convert('RGB'), (50 + j * 100 - 5 * j, 50 + i * 100 - 5 * i), hit)
            if field[i][j] == '6':
                img_field.paste(destroy.convert('RGB'), (50 + j * 100 - 5 * j, 50 + i * 100 - 5 * i), destroy)
            if field[i][j] == '7':
                img_field.paste(miss.convert('RGB'), (50 + j * 100 - 5 * j, 50 + i * 100 - 5 * i), miss)
    io = BytesIO()
    img_field.save(io, "PNG")
    io.seek(0)
    return io.read()
