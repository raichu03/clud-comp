import streamlit as st
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
import requests
from PIL import Image, ImageDraw, ImageFont
import os


ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/customvision/v3.0/Prediction/68744ebc-98ca-4e63-a84f-7c9fac0ab710/detect/iterations/an_final/image"
PREDICTION_KEY = "ebc74e4b1c8c4598ace6518951dcba92"

headers = {
    'Prediction-Key': PREDICTION_KEY,
    'Content-Type': 'application/octet-stream'
}

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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

def predict_image(image_path):
    
    image = Image.open(image_path)
    
    with open(image_path, 'rb') as image_file:
        response = requests.post(ENDPOINT, headers=headers, data=image_file)
    
    model_prediction = response.json()
    
    image_with_boxes = draw_bounding_boxes(image, model_prediction['predictions'])
    
    file_location = os.path.join(DOWNLOAD_FOLDER, "annotated_" + os.path.basename(image_path))
    with open(file_location, "wb") as f:
        image_with_boxes.save(f, format="JPEG")
    
    return file_location
