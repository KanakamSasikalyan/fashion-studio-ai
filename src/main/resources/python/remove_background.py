import sys
from PIL import Image
from rembg import remove
import io

def remove_background(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            input_image = Image.open(f)
            output_image = remove(input_image)

            with open(output_path, 'wb') as out:
                output_image.save(out, format='PNG')

        print(f"SUCCESS:{output_path}")
    except Exception as e:
        print(f"ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("ERROR:Usage: python remove_background.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    remove_background(input_path, output_path)