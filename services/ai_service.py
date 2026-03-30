"""
AI Service for content generation using Groq API.
Handles all AI-related operations including content generation and refinement.
"""

import json
import requests
from typing import Dict, Optional
import logging

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL, DEFAULT_FORMALITY, DEFAULT_HUMOR

logger = logging.getLogger(__name__)


class GroqAIService:
    """Service for interacting with Groq AI API."""
    
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.api_url = GROQ_API_URL
        
    def _get_tone_instruction(self, formality: float, humor: float) -> str:
        """Generate tone instruction based on formality and humor levels."""
        
        if formality > 0.7:
            formality_desc = "very formal and professional"
        elif formality > 0.4:
            formality_desc = "moderately formal"
        else:
            formality_desc = "casual and conversational"
        
        if humor > 0.6:
            humor_desc = "with subtle humor and wit"
        elif humor > 0.3:
            humor_desc = "with light, professional humor"
        else:
            humor_desc = "completely professional without humor"
        
        return f"Use a {formality_desc} tone {humor_desc}. Balance the tone appropriately for the platform and audience."
    
    def _get_platform_guidelines(self, platform: str) -> str:
        """Get platform-specific content guidelines."""
        guidelines = {
            "LinkedIn": """
                - Professional and formal tone
                - Focus on industry insights and thought leadership
                - Use industry-specific terminology
                - Include relevant hashtags
                - Length: 150-300 words
                - Include a call-to-action
                - Use data and statistics when relevant
            """,
            "Instagram": """
                - Visual-first approach with compelling captions
                - Conversational but professional tone
                - Use relevant hashtags (5-10 per post)
                - Length: 138-150 characters optimal
                - Include clear call-to-action
                - Use line breaks for readability
            """,
            "Twitter": """
                - Concise and impactful messaging
                - Maximum 280 characters
                - Use relevant hashtags (1-2 max)
                - Include links or media when relevant
                - Use threads for longer content
            """,
            "Facebook": """
                - Conversational and engaging tone
                - Length: 40-80 characters optimal
                - Include visual content
                - Use 1-2 relevant hashtags
                - Include questions to drive comments
            """,
            "Blog": """
                - In-depth and informative content
                - Length: 1500-2500 words optimal
                - Use headings and subheadings
                - Include relevant images
                - Optimize for SEO with keywords
            """
        }
        return guidelines.get(platform, "Follow standard professional content guidelines")
    
    def generate_content(self, prompt: str, context: Dict) -> Dict:
        """Generate platform-specific content with AI."""
        
        if not self.api_key:
            return {
                "content": "Error: Groq API key not configured. Please add your API key to config.py",
                "explanation": {"error": "API key missing"}
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        platform = context.get('platform', 'LinkedIn')
        platform_guidelines = self._get_platform_guidelines(platform)
        
        formality = context.get('formality', DEFAULT_FORMALITY)
        humor = context.get('humor', DEFAULT_HUMOR)
        tone_instruction = self._get_tone_instruction(formality, humor)
        
        enhanced_prompt = f"""
        Based on the following context, generate professional content.
        
        CONTEXT:
        - Company: {context.get('company_name', 'Unknown')}
        - Industry: {context.get('industry', 'Unknown')}
        - Target Audience: {context.get('target_audience', 'General')}
        - Brand Tone: {context.get('brand_tone', 'Professional')}
        - Platform: {platform}
        - Topic: {context.get('topic', 'General')}
        
        TONE INSTRUCTION:
        {tone_instruction}
        
        BRAND GUIDELINES:
        - Do's: {context.get('dos', [])}
        - Don'ts: {context.get('donts', [])}
        - Keywords: {context.get('keywords', [])}
        
        PLATFORM GUIDELINES:
        {platform_guidelines}
        
        Generate a {platform} post about: {prompt}
        
        Provide your response in JSON format:
        {{
            "content": "The generated content here",
            "explanation": {{
                "tone_analysis": "How the tone matches brand voice",
                "platform_optimization": "How content is optimized for {platform}",
                "unique_elements": "What makes this content unique"
            }}
        }}
        """
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "temperature": 0.8,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Extract JSON from response
                try:
                    json_str = ai_response
                    if '```json' in ai_response:
                        json_str = ai_response.split('```json')[1].split('```')[0]
                    elif '```' in ai_response:
                        json_str = ai_response.split('```')[1].split('```')[0]
                    
                    return json.loads(json_str.strip())
                except:
                    return {
                        "content": ai_response,
                        "explanation": {
                            "tone_analysis": "Generated with specified tone",
                            "platform_optimization": f"Optimized for {platform}",
                            "unique_elements": "Custom content for this topic"
                        }
                    }
            else:
                return {
                    "content": f"Error: {response.status_code} - {response.text}",
                    "explanation": {"error": "API call failed"}
                }
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return {
                "content": f"Error: {str(e)}",
                "explanation": {"error": "Exception occurred"}
            }
    
    def refine_content(self, original_content: str, feedback: str, context: Dict) -> Dict:
        """Refine content based on user feedback."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        formality = context.get('formality', DEFAULT_FORMALITY)
        humor = context.get('humor', DEFAULT_HUMOR)
        tone_instruction = self._get_tone_instruction(formality, humor)
        
        prompt = f"""
        TASK: Modify the content based on user feedback.
        
        ORIGINAL CONTENT:
        {original_content}
        
        USER FEEDBACK:
        {feedback}
        
        CONTEXT:
        - Company: {context.get('company_name', 'Unknown')}
        - Platform: {context.get('platform', 'Instagram')}
        
        TONE INSTRUCTION:
        {tone_instruction}
        
        Provide your response in JSON format:
        {{
            "content": "The modified content",
            "explanation": {{
                "changes_made": "Summary of changes",
                "feedback_addressed": "How feedback was addressed"
            }}
        }}
        """
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                try:
                    json_str = ai_response
                    if '```json' in ai_response:
                        json_str = ai_response.split('```json')[1].split('```')[0]
                    elif '```' in ai_response:
                        json_str = ai_response.split('```')[1].split('```')[0]
                    
                    return json.loads(json_str.strip())
                except:
                    return {
                        "content": ai_response,
                        "explanation": {
                            "changes_made": "Modified based on feedback",
                            "feedback_addressed": feedback
                        }
                    }
            else:
                return {
                    "content": original_content,
                    "explanation": {"error": f"Refinement failed: {response.status_code}"}
                }
        except Exception as e:
            logger.error(f"Content refinement error: {e}")
            return {
                "content": original_content,
                "explanation": {"error": str(e)}
            }