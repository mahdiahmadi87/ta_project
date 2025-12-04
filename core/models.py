from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Group(models.Model):
    """Educational groups that contain users and topics"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='ta_groups', blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Topic(models.Model):
    """Educational topics with AI-generated content"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    prompt = models.TextField(help_text="Prompt used for generating AI content")
    
    # AI-generated content
    background_image = models.ImageField(upload_to='topic_images/', null=True, blank=True)
    instructional_text = models.TextField(blank=True)
    
    # Metadata
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # AI generation status
    content_generated = models.BooleanField(default=False)
    generation_error = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.group.name})"
    
    class Meta:
        ordering = ['group', 'title']


class UserTopicProgress(models.Model):
    """Track user progress on topics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    final_score = models.IntegerField(null=True, blank=True)
    total_attempts = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # in seconds
    first_attempt_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'topic']
        ordering = ['user', 'topic']
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.title}"


class Attempt(models.Model):
    """Individual attempts on topics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    attempt_number = models.IntegerField()
    
    # Canvas data
    canvas_data = models.TextField()  # Base64 encoded PNG
    
    # Evaluation results
    score = models.IntegerField(null=True, blank=True)  # 0-20
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    
    # Updated content for incorrect attempts
    updated_background_image = models.ImageField(upload_to='attempt_images/', null=True, blank=True)
    updated_instructional_text = models.TextField(blank=True)
    
    # Timing
    time_spent = models.IntegerField()  # in seconds
    started_at = models.DateTimeField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # AI processing status
    evaluation_completed = models.BooleanField(default=False)
    evaluation_error = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['user', 'topic', 'attempt_number']
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.title} - Attempt {self.attempt_number}"


class AIGenerationLog(models.Model):
    """Log AI API calls for debugging and monitoring"""
    GENERATION_TYPES = [
        ('image', 'Image Generation'),
        ('text', 'Text Generation'),
        ('evaluation', 'Evaluation'),
    ]
    
    generation_type = models.CharField(max_length=20, choices=GENERATION_TYPES)
    prompt = models.TextField()
    response = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    api_cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Related objects
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.generation_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"