
from img2txt import generate_grayscale_for_image

from .ansi import generate_ANSI_from_pixels

from numpy import array


def pixels_to_bw(pixel_list):

    #convert all Pixel objects to (rgba) tuples
    pixels = [ [ [pixel.r, pixel.g, pixel.b, pixel.a] ] for pixel in pixel_list ]

    return generate_grayscale_for_image(array(pixels), len(pixel_list), 1, None)


def pixels_to_ansi_color(pixel_list):

    #convert all Pixel objects to (rgba) tuples
    pixels = [ [ [pixel.r, pixel.g, pixel.b, pixel.a] ] for pixel in pixel_list ]

    return generate_ANSI_from_pixels(array(pixels), len(pixel_list), 1, None)[0] + "\x1b[0m\n"
