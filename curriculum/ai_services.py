import os
import requests
from django.core.files.base import ContentFile

# Mocking the AI calls for structure. 
# Replace these functions with actual API calls (e.g., OpenAI DALL-E and GPT).

def generate_ai_text(prompt):
    """
    Generates instructional text based on the prompt.
    """
    api_key = os.getenv('AI_API_KEY')
    # Example logic:
    # response = requests.post("https://api.openai.com/v1/chat/completions", ...)
    # return response.json()...
    
    return f"Instruction generated for prompt '{prompt}': Step 1. Analyze the background. Step 2. Use the red brush to circle key elements. Step 3. Write your name in the corner."

def generate_ai_image(prompt):
    """
    Generates an image based on the prompt. 
    Returns: A ContentFile compatible with Django ImageField.
    """
    api_key = os.getenv('AI_API_KEY')
    
    # Example logic:
    # response = requests.post("https://api.openai.com/v1/images/generations", ...)
    # image_url = response.json()['data'][0]['url']
    # image_content = requests.get(image_url).content
    
    # For this demo, we return a placeholder logic or dummy bytes
    # In production, fetch the bytes from the generated URL
    import io
    from PIL import Image, ImageDraw
    
    img = Image.new('RGB', (800, 600), color=(240, 240, 240))
    d = ImageDraw.Draw(img)
    d.text((10,10), f"AI Background: {prompt}", fill=(0,0,0))
    
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    return ContentFile(img_io.getvalue(), name=f"ai_gen_{prompt[:10]}.png")