init python:
    def get_image_size(rwops):
        """
        Returns the width and height of the given Ren'Py RWops object
        representing an image.

        This function should not be called directly, it is here to be used by
        the [spritesheet_animation] function.

        Arguments:
        rwops (RWops): RWops object returned by calling `renpy.open_file` on an
        image file.

        Returns:
        width (int): Width of the input image file
        height (int): Height of the input image file
        """
        import struct
        import imghdr

        head = rwops.read(24)

        if len(head) != 24:
            raise Exception("Invalid or corrupt image file: " + rwops.name)

        if imghdr.what(rwops.name) == 'png':
            check = struct.unpack('>i', head[4:8])[0]

            if check != 0x0d0a1a0a:
                raise Exception("Invalid PNG file: " + rwops.name)

            width, height = struct.unpack('>ii', head[16:24])

        elif imghdr.what(rwops.name) == 'jpeg':
            try:
                rwops.seek(0)
                size = 2
                ftype = 0

                while not 0xc0 <= ftype <= 0xcf:
                    rwops.seek(size, 1)
                    byte = rwops.read(1)
                    while ord(byte) == 0xff:
                        byte = rwops.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', rwops.read(2))[0] - 2

                rwops.seek(1, 1)
                height, width = struct.unpack('>HH', rwops.read(4))

            except Exception:
                raise Exception("Failed to read JPEG headers from file: " + rwops.name)

        else:
            raise Exception("unsupported image type on file: " + rwops.name)

        return width, height

    def spritesheet_animation(image_path, x_sprite_count, y_sprite_count, **kwargs):
        """
        Generates an animation from the given sprite file path.  The given path
        MUST be a valid path relative to the game directory including the file
        extension, e.g. "images/animation.png".

        This method supports the following file types: [ `"png"`, `"jpg"` ]

        Arguments:
        ----------
        image_path (str): Path to the sprite sheet image file.
        
        x_sprite_count (int): Number of sprites that appear on the sprite
        sheet's x axis.
        
        y_sprite_count (int): Number of sprites that appear on the sprite
        sheet's y axis.

        Keyword Arguments:
        ------------------
        fps (int|float): Frames per second for the animation.  This argument is
        incompatible with `pause`; using both will cause an error.  Defaults to
        `30`.
        
        pause (float): How long to pause between each frame.  This argument is
        incompatible with `fps`; using both will cause an error.  Defaults to
        `None`.
        
        looping (bool): Whether the animation should loop.  Defaults to
        `False`.
        
        hold_last_frame (bool): Whether the animation should hold on the last
        frame.  Defaults to `False`.

        Returns:
        --------
        image_name (str): The name of the generated animation.
        """
        from uuid import uuid4

        if "fps" in kwargs:
            if "pause" in kwargs:
                raise Exception("cannot set both \"fps\" and \"pause\".")
            else:
                pause = 1.0 / float(kwargs["fps"])
        elif "pause" in kwargs:
            pause = float(kwargs["pause"])
        else:
            pause = 1.0 / 30

        looping = bool(kwargs["looping"]) if "looping" in kwargs else False

        hold_last_frame = bool(kwargs["hold_last_frame"]) if "hold_last_frame" in kwargs else False

        with renpy.open_file(image_path) as handle:
            full_width, full_height = get_image_size(handle)

        sprite_width = int(full_width / x_sprite_count)
        sprite_height = int(full_height / y_sprite_count)
        sprite_count = x_sprite_count * y_sprite_count

        img = Image(image_path)

        frames = []

        current_x = 0
        current_y = 0

        for i in range(sprite_count):

            if current_x == x_sprite_count:
                current_y += 1
                current_x = 0

            frames.append(Transform(img, crop=(current_x * sprite_width, current_y * sprite_height, sprite_width, sprite_height)))
            frames.append(pause)

            current_x += 1

        if not looping:
            if not hold_last_frame:
                renpy.image("clear_solid_last_animation_frame", Solid("#ffffff00"))
                frames.append("clear_solid_last_animation_frame")
            else:
                frames.pop()

        image_name = str(uuid4())

        renpy.image(image_name, Animation(*frames))

        return image_name

image toast = spritesheet_animation("images/explosion.png", 8, 6, fps=45)
