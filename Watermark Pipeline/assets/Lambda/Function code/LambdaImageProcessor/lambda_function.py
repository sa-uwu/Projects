import boto3
import logging 
from PIL import Image, ImageDraw, ImageFont
import os
import io
import urllib.parse

# Initialize S3 client
s3 = boto3.client('s3')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Config via env vars
output_bucket= os.environ.get('OutputBucket')  

# --- Configuration for font sizes, padding, and colors ---
FONT_SIZES = {
    'xs':20,
    'small': 30,
    'medium': 40,
    'large': 75,
    'xl': 100,
    'xxl': 120
}
# Define a fallback default if no valid size is provided or parsed
DEFAULT_PIXEL_FONT_SIZE = 70 # A sensible default pixel size if 'Size' tag is invalid

# Fixed border padding in pixels for more robust spacing
BORDER_PADDING_PIXELS = 70 

# Define watermark colors (RGBA for transparency)
WATERMARK_COLORS = {
    'white': (255, 255, 255, 128), # Semi-transparent white
    'black': (0, 0, 0, 128),     # Semi-transparent black
    'red': (255, 0, 0, 128),     # Semi-transparent red
    'blue': (0, 0, 255, 128),    # Semi-transparent blue
    'green': (0, 255, 0, 128),   # Semi-transparent green
    'yellow': (255, 255, 0, 128) # Semi-transparent yellow
}
DEFAULT_WATERMARK_COLOR = WATERMARK_COLORS['white']

def lambda_handler(event, context):
    logger.info("Lambda function started.")
    
    # Store all tags retrieved from the input object to propagate them
    propagated_tags = [] 

    try:
        # Log the received event
        logger.info(f"Received event: {event}")

        # Get the bucket name and object key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        file_name = object_key.split("/")[-1]
        logger.info(f"Processing file: {file_name} from bucket: {bucket_name}")

        # Validate the file format
        if not object_key.lower().endswith(('.png', '.jpg', '.jpeg')):
            logger.error("Unsupported file format. Only PNG and JPEG are allowed.")
            return {
                'statusCode': 400,
                'body': "Unsupported file format. Please upload a PNG or JPEG file."
            }
        
        # --- Retrieve ALL S3 Object Tags for watermark text, position, font size, color, and email ---
        watermark_text = os.environ.get('WATERMARK_TEXT', '© The Saau Media Company')
        watermark_position = 'bottom-right'
        watermark_font_size_value = None # Will store either a string key (s,m,l) or a pixel integer
        watermark_color_key = 'white'
        email_address = None 

        logger.info(f"Initial defaults: text='{watermark_text}', position='{watermark_position}', font_size_key_or_pixel='{watermark_font_size_value}', color_key='{watermark_color_key}', email_address='{email_address}'")

        try:
            # Get object tags from S3
            response = s3.get_object_tagging(Bucket=bucket_name, Key=object_key)
            tags = response.get('TagSet', [])
            logger.info(f"Retrieved S3 object tags: {tags}")

            # Iterate through tags and set values (case-insensitive for the key comparison)
            for tag in tags:
                tag_key_lower = tag.get('Key', '').lower() 
                
                # Add the original tag to the list for propagation
                propagated_tags.append({'Key': tag.get('Key'), 'Value': tag.get('Value')})

                if tag_key_lower == 'text':
                    watermark_text = tag.get('Value')
                    logger.info(f"Overriding watermark text from 'Text' tag: '{watermark_text}'")
                elif tag_key_lower == 'position':
                    watermark_position = tag.get('Value').lower() 
                    logger.info(f"Overriding watermark position from 'Position' tag: '{watermark_position}'")
                elif tag_key_lower == 'size':
                    watermark_font_size_value = tag.get('Value') # Keep original casing for now
                    logger.info(f"Retrieved font size value from 'Size' tag: '{watermark_font_size_value}'")
                elif tag_key_lower == 'color':
                    watermark_color_key = tag.get('Value').lower() 
                    logger.info(f"Overriding watermark color key from 'Color' tag: '{watermark_color_key}'")
                elif tag_key_lower == 'email': 
                    email_address = tag.get('Value')
                    logger.info(f"Captured email address from 'Email' tag: '{email_address}'")
            
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                logger.error(f"Access Denied: Lambda role needs s3:GetObjectTagging permission on {bucket_name}/{object_key}. Using default values.")
            elif e.response['Error']['Code'] == 'NoSuchKey': 
                logger.warning(f"Object {object_key} not found for tag retrieval. Using default values.")
            else:
                logger.error(f"Error retrieving S3 object tags for {object_key}: {str(e)}. Using default values.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during tag retrieval: {str(e)}. Using default values.")
        
        # --- NEW: Map font size string to pixel value or parse as integer ---
        watermark_text_size = DEFAULT_PIXEL_FONT_SIZE # Start with a strong default
        if watermark_font_size_value:
            try:
                # Try to convert to integer (pixel size)
                watermark_text_size = int(watermark_font_size_value)
                logger.info(f"Parsed font size as pixel value: {watermark_text_size}")
            except ValueError:
                # If not an integer, try lookup in FONT_SIZES (case-insensitive)
                watermark_text_size = FONT_SIZES.get(watermark_font_size_value.lower(), DEFAULT_PIXEL_FONT_SIZE)
                logger.info(f"Looked up font size key '{watermark_font_size_value.lower()}', result: {watermark_text_size}")

        logger.info(f"Actual watermark text size (pixels): {watermark_text_size}")
        # --- END NEW ---

        # Map watermark color string to RGBA tuple
        watermark_fill_color = WATERMARK_COLORS.get(watermark_color_key, DEFAULT_WATERMARK_COLOR)
        logger.info(f"Actual watermark fill color (RGBA): {watermark_fill_color}")

        # Download the image from S3
        download_stream = io.BytesIO()
        try:
            s3.download_fileobj(bucket_name, object_key, download_stream)
            download_stream.seek(0)
            logger.info("Image downloaded successfully.")
        except Exception as e:
            logger.error(f"Error downloading image from S3: {str(e)}")
            return {
                'statusCode': 404,
                'body': "The specified file could not be found in the bucket."
            }

        # Open the image using PIL
        image = Image.open(download_stream).convert("RGBA")  # Convert to RGBA to handle transparency
        logger.info(f"Image opened successfully. Format: {image.format}, Size: {image.size}")

        # Font path
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" 
        
        # Load the font
        try:
            font = ImageFont.truetype(font_path, size=watermark_text_size)
            logger.info(f"Font loaded successfully: {font_path}")
        except IOError:
            logger.error(f"Font loading failed for {font_path}. Falling back to default font.")
            font = ImageFont.load_default()

        # Create a transparent overlay for the watermark
        txt = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)

        # Calculate text size using textbbox (bounding box)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        logger.info(f"Calculated text size: width={text_width}, height={text_height}")

        # Use fixed border padding in pixels
        pad_x = BORDER_PADDING_PIXELS
        pad_y = BORDER_PADDING_PIXELS
        logger.info(f"Using fixed border padding: pad_x={pad_x}, pad_y={pad_y}")

        # Calculate initial watermark position based on tags
        x, y = 0, 0 

        img_width, img_height = image.size

        if watermark_position == 'top-left':
            x = pad_x
            y = pad_y
        elif watermark_position == 'top':
            x = (img_width - text_width) // 2
            y = pad_y
        elif watermark_position == 'top-right':
            x = img_width - text_width - pad_x
            y = pad_y
        elif watermark_position == 'right':
            x = img_width - text_width - pad_x
            y = (img_height - text_height) // 2
        elif watermark_position == 'center':
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
        elif watermark_position == 'left':
            x = pad_x
            y = (img_height - text_height) // 2
        elif watermark_position == 'bottom-left':
            x = pad_x
            y = img_height - text_height - pad_y
        elif watermark_position == 'bottom':
            x = (img_width - text_width) // 2
            y = img_height - text_height - pad_y
        else: # Default to bottom-right if invalid or missing
            x = img_width - text_width - pad_x
            y = img_height - text_height - pad_y
            logger.warning(f"Invalid or missing watermark position '{watermark_position}'. Defaulting to 'bottom-right'.")
        
        # Clamp x and y coordinates to ensure watermark stays within bounds
        x = max(pad_x, min(x, img_width - text_width - pad_x))
        y = max(pad_y, min(y, img_height - text_height - pad_y))

        logger.info(f"Watermark final position: x={x}, y={y}")

        # Draw the watermark text
        draw.text((x, y), watermark_text, fill=watermark_fill_color, font=font) 
        logger.info("Watermark added to the overlay.")

        # Composite the overlay with the original image
        watermarked = Image.alpha_composite(image, txt)

        # Convert back to original mode for saving if necessary
        if image.mode != "RGBA":
            watermarked = watermarked.convert(image.mode)

        # Determine output format for saving
        image_format = image.format
        if not image_format: 
            if object_key.lower().endswith('.png'):
                image_format = 'PNG'
            else: 
                image_format = 'JPEG' 
        logger.info(f"Saving watermarked image in format: {image_format}")

        # Save the watermarked image to a BytesIO stream
        output_stream = io.BytesIO()
        try:
            watermarked.save(output_stream, format=str(image_format))
            output_stream.seek(0)
            logger.info("Watermarked image saved to output stream.")
        except ValueError as e:
            logger.error(f"Error saving watermarked image: {str(e)}")
            return {
                'statusCode': 500,
                'body': "Error saving the watermarked image."
            }

        # Define the output key
        output_key = f"processed/{file_name}"

        # Prepare tags for the output object
        output_tags_string = '&'.join([
            f"{urllib.parse.quote_plus(tag['Key'])}={urllib.parse.quote_plus(tag['Value'])}"
            for tag in propagated_tags
        ])
        logger.info(f"Tags to propagate to output object: {output_tags_string}")

        # Upload the watermarked image to the output bucket using put_object with Tagging
        s3.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=output_stream,
            ContentType=f"image/{image_format.lower()}",
            Tagging=output_tags_string 
        )
        logger.info(f"Watermarked image uploaded to bucket: {output_bucket}, key: {output_key} with propagated tags.")

        return {
            'statusCode': 200,
            'body': f"Image {object_key} processed and saved to {output_key}"
        }

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': "An error occurred while processing the image."
        }
