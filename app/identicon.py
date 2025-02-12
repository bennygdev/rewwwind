import hashlib
import random
import png
from itertools import chain

palette = {
    0: (255, 255, 255),
    1: (101, 155, 216),
    2: (255, 119, 109),
    3: (255, 215, 147),
    4: (158, 239, 174),
    5: (201, 157, 186)
}

def create_identicon(username, filename, avatar_size=5, img_size_per_cell=100):
    """Creates and writes an identicon to disk
    Arguments:
        - username (str): username for which the identicon should be created
        - filename (str): file to which the image should be written
        - avatar_size (int): number of cells in width/height (default: 5)
        - img_size_per_cell (int): pixels per cell (default: 100)
    """
    # Hash username to use as seed
    username_hash = hashlib.md5(username.encode("utf-8"))
    random.seed(username_hash.hexdigest())
    
    # Select random color among the 5 defined colors
    color = random.randint(1, 5)

    # Create the left half of the avatar
    avatar_base_width = (avatar_size + 2) // 2 + avatar_size % 2
    
    # Create first blank row (padding)
    avatar_base = [[0 for _ in range(avatar_base_width)]]
    
    # Create actual avatar
    avatar_base += [[0] +  # blank left column for padding
                    [random.randint(0, 1)
                     for _ in range(avatar_base_width - 1)]
                    for _ in range(avatar_size)]
    
    # Create last blank row (padding)
    avatar_base += [[0 for _ in range(avatar_base_width)]]

    # Create full-width binary version of avatar
    avatar_bin = [[row[i] if i < avatar_base_width
                   else row[avatar_size + 1 - i]
                   for i in range(avatar_size + 2)]
                  for row in avatar_base]

    # Create RGB avatar
    avatar = [[palette[color * pixel] for pixel in row] for row in avatar_bin]
    
    # Resize avatar
    avatar = _resize_avatar(avatar, avatar_size, img_size_per_cell)
    
    # Flatten RGB values for pypng
    flat_avatar = []
    for row in avatar:
        flat_row = []
        for pixel in row:
            flat_row.extend(pixel)
        flat_avatar.append(flat_row)

    # Save the image
    w = len(flat_avatar[0]) // 3  # Width is the length of a row divided by 3 (RGB)
    h = len(flat_avatar)          # Height is the number of rows
    
    with open(filename, 'wb') as f:
        w = png.Writer(width=w, height=h, greyscale=False)
        w.write(f, flat_avatar)

def _resize_avatar(avatar, avatar_size, img_size_per_cell):
    """Resizes avatar using nearest-neighbor scaling"""
    img_size = img_size_per_cell * (avatar_size + 2)
    return [[avatar[i // img_size_per_cell][j // img_size_per_cell]
             for j in range(img_size)]
            for i in range(img_size)]