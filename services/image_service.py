"""
Cloudflare Image Generation Service.
Handles AI-powered image generation using Stable Diffusion.
"""

import requests
from io import BytesIO
from PIL import Image
from typing import Optional

from config import CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN


class CloudflareImageGenerator:
    """Generate images using Cloudflare's Stable Diffusion XL."""
    
    def __init__(self):
        self.account_id = CLOUDFLARE_ACCOUNT_ID
        self.api_token = CLOUDFLARE_API_TOKEN
        self.model = "@cf/stabilityai/stable-diffusion-xl-base-1.0"
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/"
    
    def generate_image(self, prompt: str, style: str = "photorealistic") -> Optional[Image.Image]:
        """Generate image using Cloudflare's Stable Diffusion XL."""
        
        if not self.account_id or not self.api_token:
            print("Cloudflare credentials not configured")
            return None
        
        url = f"{self.base_url}{self.model}"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Style prompts
        style_prompts = {
            "photorealistic": "ultra realistic, highly detailed, 8k, professional photography",
            "digital art": "digital art, trending on artstation, highly detailed",
            "watercolor": "watercolor painting, artistic, soft colors",
            "sketch": "pencil sketch, black and white, detailed drawing",
            "3D render": "3D render, cgi, octane render, blender, highly detailed",
            "cinematic": "cinematic, movie poster style, dramatic lighting",
            "minimalist": "minimalist, simple, clean design, white background",
            "business": "professional business style, corporate, clean, modern"
        }
        
        style_suffix = style_prompts.get(style, style_prompts["photorealistic"])
        enhanced_prompt = f"{prompt}, {style_suffix}, professional quality, suitable for social media"
        
        payload = {"prompt": enhanced_prompt}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                print(f"Cloudflare API Error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("Request timed out")
            return None
        except Exception as e:
            print(f"Image generation error: {e}")
            return None