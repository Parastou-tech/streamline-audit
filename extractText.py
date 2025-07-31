import boto3
def extractText(file):
    # Use the profile you just confirmed works
    session = boto3.Session(profile_name="cpisb_IsbUsersPS-920016976961") # replace with yours
    textract = session.client("textract", region_name="us-west-2")

    # Load an image file from your local folder
    with open(file, "rb") as f:
        img_bytes = f.read()

    # Call Textract to detect text
    response = textract.detect_document_text(Document={'Bytes': img_bytes})

    # Collect all lines into a list
    lines = [block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE']

    # Join the lines into a single string (with line breaks)
    full_text = '\n'.join(lines)

    # Now you can use `full_text` as a single string
    return(full_text)