import boto3
import logging
import os

# Initialize AWS clients
s3 = boto3.client('s3')
ses = boto3.client('ses')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Config via env vars
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')  
OutputBucket = os.environ.get('OutputBucket')

# ===============================
# Load templates during initialization
# ===============================
def load_template_file(filename):
    """Read the template file content."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading template '{filename}': {e}")
        return None

HTML_TEMPLATE = load_template_file("email_template.html")
TEXT_TEMPLATE = load_template_file("email_template.txt")

if HTML_TEMPLATE and TEXT_TEMPLATE:
    logger.info("Email templates loaded successfully during initialization.")
else:
    logger.warning("One or more templates could not be loaded at initialization.")

# ===============================
# Lambda handler
# ===============================
def lambda_handler(event, context):
    logger.info("SES Notifier Lambda function started.")

    recipient_email = None
    object_key = None

    try:
        logger.info(f"Received event: {event}")

        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        image_filename = object_key.split('/')[-1]

        logger.info(f"Processing file: {object_key} from bucket: {bucket_name}")

        if bucket_name != OutputBucket:
            logger.error(f"Unexpected bucket '{bucket_name}'. Expected '{OutputBucket}'. Exiting.")
            return {'statusCode': 400, 'body': "Lambda triggered by wrong bucket."}

        # --- Retrieve recipient email from S3 object tags ---
        response = s3.get_object_tagging(Bucket=bucket_name, Key=object_key)
        tags = response.get('TagSet', [])
        for tag in tags:
            if tag.get('Key', '').lower() == 'email':
                recipient_email = tag.get('Value')
                break

        if not recipient_email:
            logger.warning(f"No 'Email' tag found for {object_key}. Cannot send notification email.")
            return {'statusCode': 200, 'body': "No recipient email found in tags. Skipping notification."}

        # --- Generate presigned URLs ---
        view_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=3600
        )

        download_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                'ResponseContentDisposition': f'attachment; filename="{image_filename}"'
            },
            ExpiresIn=3600
        )

        if not SENDER_EMAIL:
            logger.error("SENDER_EMAIL env var is not set.")
            return {'statusCode': 500, 'body': "Sender email not configured."}

        # --- Prepare email ---
        subject = "Your Watermarked Image is Ready!"
        replacements = {
            "image_filename": image_filename,
            "view_url": view_url,
            "download_url": download_url
        }

        def replace_placeholders(template):
            if not template:
                return ""
            result = template
            for key, value in replacements.items():
                result = result.replace(f"{{{{ {key} }}}}", value)
            return result

        body_text = replace_placeholders(TEXT_TEMPLATE)
        body_html = replace_placeholders(HTML_TEMPLATE)

        # --- Send email ---
        response = ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )

        logger.info(f"Email sent to {recipient_email}. MessageId: {response['MessageId']}")
        return {'statusCode': 200, 'body': f"Email sent to {recipient_email} for {object_key}"}

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return {'statusCode': 500, 'body': "Unhandled error occurred."}
