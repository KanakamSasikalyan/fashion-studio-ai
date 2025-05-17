# remove_background.py (updated version)
import sys
import os
from PIL import Image
from rembg import remove
import io
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BackgroundRemoval')

def process_image(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            input_image = Image.open(f)
            output_image = remove(input_image)

            # Save to bytes buffer instead of file
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Write to file (temporary for Java to read)
            with open(output_path, 'wb') as out:
                out.write(img_byte_arr)

            print(f"SUCCESS:{output_path}")
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(f"ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("ERROR:Usage: python remove_background.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    process_image(input_path, output_path)










'''import sys
import os
from PIL import Image
from rembg import remove
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BackgroundRemoval')

def upload_to_imagekit(file_path, filename):
    imagekit = ImageKit(
        public_key='public_kFHuvOaiMWhxtEDbGKOGTBw9E9g=',
        private_key='private_bRat8BgH2PReRgIbtw8tp1pFze4=',
        url_endpoint='https://ik.imagekit.io/sp7ub8zm6/sp7ub8zm6'
    )

    with open(file_path, 'rb') as file:
        upload = imagekit.upload_file(
            file=file,
            file_name=filename,
            options=UploadFileRequestOptions(
                folder="/processed_images/",
                is_private_file=False,
                use_unique_file_name=True
            )
        )

        if upload.response_metadata.http_status_code == 200:
            return upload.url
        raise Exception(f"ImageKit upload failed: {upload.response_metadata.raw}")

def process_image(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            input_image = Image.open(f)
            output_image = remove(input_image)

            # Save processed image temporarily
            output_image.save(output_path, format='PNG')

            # Upload to ImageKit
            filename = os.path.basename(output_path)
            image_url = upload_to_imagekit(output_path, filename)

            # Clean up temp file
            os.remove(output_path)

            print(f"SUCCESS:{image_url}")
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(f"ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("ERROR:Usage: python remove_background.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    process_image(input_path, output_path)'''




####################################Old-Code##########################################
'''import sys
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
    remove_background(input_path, output_path)'''