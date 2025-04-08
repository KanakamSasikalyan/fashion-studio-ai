from PIL import Image, ImageFilter, ImageOps
import numpy as np

def apply_texture_effect(image, style):
    """CPU-only texture effects"""
    effects = {
        "cotton": lambda img: img.filter(ImageFilter.SMOOTH),
        "denim": lambda img: ImageOps.posterize(img, 4),
        "silk": lambda img: img.filter(ImageFilter.GaussianBlur(radius=1)),
        "leather": lambda img: ImageOps.autocontrast(img, cutoff=5)
    }
    return effects.get(style, lambda x: x)(image)