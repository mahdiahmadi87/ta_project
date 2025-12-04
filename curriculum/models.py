from django.db import models
from django.contrib.auth.models import Group
from .ai_services import generate_ai_text, generate_ai_image

class Topic(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Short description for the home page.")
    
    # Groups that can access this topic
    groups = models.ManyToManyField(Group, related_name='topics')
    
    # AI Generation Fields
    prompt = models.TextField(help_text="Prompt used to generate background and instructions.")
    
    # Assets (Auto-generated)
    generated_instruction = models.TextField(blank=True, editable=False)
    generated_background = models.ImageField(upload_to='topic_backgrounds/', blank=True, editable=False)

    def save(self, *args, **kwargs):
        # Check if this is a new object or if the prompt has changed
        is_new = self.pk is None
        if not is_new:
            old_instance = Topic.objects.get(pk=self.pk)
            prompt_changed = old_instance.prompt != self.prompt
        else:
            prompt_changed = True

        # Trigger AI generation only if prompt changed or assets are missing
        if prompt_changed or not self.generated_background:
            try:
                # 1. Generate Text
                self.generated_instruction = generate_ai_text(self.prompt)
                
                # 2. Generate Image
                # Note: In production, consider using Celery for async processing 
                # to avoid blocking the Admin save.
                image_file = generate_ai_image(self.prompt)
                self.generated_background.save(f"{self.title}_bg.png", image_file, save=False)
            except Exception as e:
                # Handle API failures gracefully
                print(f"AI Generation failed: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title