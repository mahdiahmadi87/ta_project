import requests
import base64
import json
import os
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from .models import AIGenerationLog, Topic, Attempt
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service class for AI API interactions"""
    
    @staticmethod
    def generate_image(prompt, topic=None, attempt=None):
        """Generate image using AI API"""
        try:
            headers = {
                'Authorization': f'Bearer {settings.IMAGE_GENERATION_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': settings.IMAGE_MODEL,
                'prompt': prompt,
                'n': 1,
                'size': '1024x1024',
                'quality': 'standard'
            }
            
            # Log the request
            log_entry = AIGenerationLog.objects.create(
                generation_type='image',
                prompt=prompt,
                topic=topic,
                attempt=attempt
            )
            
            response = requests.post(settings.IMAGE_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data['data'][0]['url']
                
                # Download the image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    # Update log
                    log_entry.success = True
                    log_entry.response = json.dumps(data)
                    log_entry.save()
                    
                    return img_response.content
                else:
                    raise Exception(f"Failed to download image: {img_response.status_code}")
            else:
                error_msg = f"Image generation failed: {response.status_code} - {response.text}"
                log_entry.error_message = error_msg
                log_entry.save()
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            if 'log_entry' in locals():
                log_entry.error_message = str(e)
                log_entry.save()
            raise
    
    @staticmethod
    def generate_text(prompt, topic=None, attempt=None):
        """Generate instructional text using AI API"""
        try:
            headers = {
                'Authorization': f'Bearer {settings.TEXT_GENERATION_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': settings.TEXT_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an educational assistant. Generate clear, friendly, step-by-step instructional text for students.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            # Log the request
            log_entry = AIGenerationLog.objects.create(
                generation_type='text',
                prompt=prompt,
                topic=topic,
                attempt=attempt
            )
            
            response = requests.post(settings.TEXT_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data['choices'][0]['message']['content']
                
                # Update log
                log_entry.success = True
                log_entry.response = generated_text
                log_entry.save()
                
                return generated_text
            else:
                error_msg = f"Text generation failed: {response.status_code} - {response.text}"
                log_entry.error_message = error_msg
                log_entry.save()
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Text generation error: {str(e)}")
            if 'log_entry' in locals():
                log_entry.error_message = str(e)
                log_entry.save()
            raise
    
    @staticmethod
    def evaluate_drawing(canvas_data, topic_prompt, instructional_text, background_description, attempt=None):
        """Evaluate user drawing and provide feedback"""
        try:
            evaluation_prompt = f"""
            You are an educational evaluator. A student has completed a drawing exercise.
            
            Original Topic: {topic_prompt}
            Instructional Text: {instructional_text}
            Background Description: {background_description}
            
            The student has submitted a drawing (canvas data provided as base64 PNG).
            
            Please evaluate the drawing and provide:
            1. A score from 0-20 (20 being perfect)
            2. Whether the submission is correct (true/false)
            3. Detailed feedback explaining what is correct and what needs improvement
            4. If incorrect, specify exactly what elements need to be redrawn
            
            Respond in JSON format:
            {{
                "score": <0-20>,
                "is_correct": <true/false>,
                "feedback": "<detailed explanation>",
                "corrections_needed": "<specific corrections if incorrect>"
            }}
            
            Canvas Data: {canvas_data[:100]}... (truncated for brevity)
            """
            
            headers = {
                'Authorization': f'Bearer {settings.TEXT_GENERATION_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': settings.TEXT_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an educational evaluator. Analyze student drawings and provide constructive feedback in JSON format.'
                    },
                    {
                        'role': 'user',
                        'content': evaluation_prompt
                    }
                ],
                'max_tokens': 800,
                'temperature': 0.3
            }
            
            # Log the request
            log_entry = AIGenerationLog.objects.create(
                generation_type='evaluation',
                prompt=evaluation_prompt,
                attempt=attempt
            )
            
            response = requests.post(settings.TEXT_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                evaluation_text = data['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    evaluation_result = json.loads(evaluation_text)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    evaluation_result = {
                        'score': 10,
                        'is_correct': False,
                        'feedback': evaluation_text,
                        'corrections_needed': 'Please review your drawing and try again.'
                    }
                
                # Update log
                log_entry.success = True
                log_entry.response = evaluation_text
                log_entry.save()
                
                return evaluation_result
            else:
                error_msg = f"Evaluation failed: {response.status_code} - {response.text}"
                log_entry.error_message = error_msg
                log_entry.save()
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}")
            if 'log_entry' in locals():
                log_entry.error_message = str(e)
                log_entry.save()
            raise


class TopicContentGenerator:
    """Service for generating topic content"""
    
    @staticmethod
    def generate_topic_content(topic):
        """Generate background image and instructional text for a topic"""
        try:
            # Generate background image
            image_prompt = f"Educational illustration: {topic.prompt}. Create a clear, simple diagram suitable for student interaction."
            image_data = AIService.generate_image(image_prompt, topic=topic)
            
            # Save image
            image_file = ContentFile(image_data)
            topic.background_image.save(
                f'topic_{topic.id}_background.png',
                image_file,
                save=False
            )
            
            # Generate instructional text
            text_prompt = f"""
            Create clear, step-by-step instructional text for students working on this topic:
            {topic.prompt}
            
            The instructions should:
            1. Explain what the student needs to draw
            2. Provide clear guidance on colors, directions, and elements
            3. Be encouraging and educational
            4. Be suitable for interactive canvas drawing
            """
            
            instructional_text = AIService.generate_text(text_prompt, topic=topic)
            topic.instructional_text = instructional_text
            
            # Mark as generated
            topic.content_generated = True
            topic.save()
            
            return True
            
        except Exception as e:
            topic.generation_error = str(e)
            topic.save()
            logger.error(f"Topic content generation failed for topic {topic.id}: {str(e)}")
            return False


class FeedbackGenerator:
    """Service for generating updated content based on feedback"""
    
    @staticmethod
    def generate_corrected_content(attempt, evaluation_result):
        """Generate corrected image and text for incorrect attempts"""
        try:
            if evaluation_result['is_correct']:
                return True
            
            # Generate corrected image
            corrections = evaluation_result.get('corrections_needed', '')
            corrected_image_prompt = f"""
            Based on the original topic: {attempt.topic.prompt}
            
            Generate a corrected version that shows:
            - The correct elements the student drew properly
            - Corrections for the mistakes: {corrections}
            - Clear visual guidance for what needs to be redrawn
            
            Make it educational and visually clear for the student to understand their mistakes.
            """
            
            image_data = AIService.generate_image(corrected_image_prompt, attempt=attempt)
            
            # Save corrected image
            image_file = ContentFile(image_data)
            attempt.updated_background_image.save(
                f'attempt_{attempt.id}_corrected.png',
                image_file,
                save=False
            )
            
            # Generate updated instructional text
            text_prompt = f"""
            The student made some mistakes in their drawing. Generate encouraging, specific instructions:
            
            Original feedback: {evaluation_result['feedback']}
            Corrections needed: {corrections}
            
            Create friendly, step-by-step guidance that:
            1. Acknowledges what they did correctly
            2. Clearly explains what needs to be fixed
            3. Provides specific instructions for corrections
            4. Encourages them to try again
            """
            
            updated_text = AIService.generate_text(text_prompt, attempt=attempt)
            attempt.updated_instructional_text = updated_text
            attempt.save()
            
            return True
            
        except Exception as e:
            attempt.evaluation_error = str(e)
            attempt.save()
            logger.error(f"Corrected content generation failed for attempt {attempt.id}: {str(e)}")
            return False