import streamlit as st
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
import requests
from io import BytesIO

# Load environment variables
load_dotenv()
prediction_key = os.getenv('PredictionKey')

# Set up request headers
headers = {
    'Prediction-Key': prediction_key,
    'Content-Type': 'application/octet-stream'
}

url_image = "https://centralindia.api.cognitive.microsoft.com/customvision/v3.0/Prediction/68744ebc-98ca-4e63-a84f-7c9fac0ab710/detect/iterations/an_final/url"
file_image = "https://centralindia.api.cognitive.microsoft.com/customvision/v3.0/Prediction/68744ebc-98ca-4e63-a84f-7c9fac0ab710/detect/iterations/an_final/image"


from PIL import Image, ImageDraw, ImageFont

def draw_bounding_boxes(image, predictions, confidence_threshold=0.5, color='red', line_width=1):
    """
    This function draws bounding boxes around objects identified in predictions on the image.

    Args:
        image: The image on which bounding boxes need to be drawn.
        predictions: A list of predictions, where each prediction is a dictionary containing 
                     information about the detected object (e.g., bounding box, class label, confidence score).
        confidence_threshold: The minimum confidence score for a prediction to be visualized (default: 0.5).
        color: The color of the bounding boxes (default: 'magenta').
        line_width: The width of the lines for the bounding boxes (default: 1).

    Returns:
        The modified image with drawn bounding boxes.
    """  

    draw = ImageDraw.Draw(image)
    text_offset = 2  # Adjust this value to control the text position above the box
    font = ImageFont.load_default()  # Load a default font

    for prediction in predictions:
        if prediction['probability'] > confidence_threshold:
            left = prediction['boundingBox']['left'] * image.width
            top = prediction['boundingBox']['top'] * image.height
            width = prediction['boundingBox']['width'] * image.width
            height = prediction['boundingBox']['height'] * image.height

            # Draw bounding box
            draw.rectangle([left, top, left + width, top + height], outline=color, width=line_width)

            # Modify text format and position
            text_format = f"{prediction['tagName']}: {prediction['probability']:.2f}"
            # Get text size using textbbox
            bbox = draw.textbbox((left, top), text_format, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.rectangle([left, top - text_height - text_offset, left + text_width, top - text_offset], fill='red')  # Draw pink background
            draw.text((left, top - text_height - text_offset), text_format, fill='white', font=font)  # Write white text above box

    return image


def main():
    st.title("Object Detection with Custom Vision")

    # Upload image or enter URL
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    image_url = st.text_input("Or enter an image URL")

    if uploaded_file is not None or image_url:
        if uploaded_file:
            image = Image.open(uploaded_file)
            image_data = uploaded_file.getvalue()
            st.image(image, caption="Uploaded Image", use_column_width=True)
            response = requests.post(file_image, headers=headers, data=image_data)
        elif image_url:
            response = requests.post(
                url_image,
                headers={'Prediction-Key': prediction_key, 'Content-Type': 'application/json'},
                json={"Url": image_url}
            )
            image = Image.open(BytesIO(requests.get(image_url).content))
            st.image(image, caption="Image from URL", use_column_width=True)
        
        # Process the response
        if response.status_code == 200:
            results = response.json()
            predictions = results['predictions']

            # Draw bounding boxes on the image
            image_with_boxes = draw_bounding_boxes(image, predictions)

            # Display the image with bounding boxes
            st.image(image_with_boxes, caption="Image with Bounding Boxes", use_column_width=True)
        else:
            st.error(f"Request failed with status code {response.status_code}")
            st.error(response.text)

if __name__ == "__main__":
    main()