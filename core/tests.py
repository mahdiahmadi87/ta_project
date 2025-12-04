from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Group, Topic, UserTopicProgress, Attempt
import json


class TASystemTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass',
            is_staff=True,
            is_superuser=True
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            password='testpass',
            first_name='Test',
            last_name='Student'
        )
        
        # Create group
        self.group = Group.objects.create(
            name='Test Group',
            description='Test group for unit tests',
            created_by=self.admin_user
        )
        self.group.members.add(self.student_user)
        
        # Create topic
        self.topic = Topic.objects.create(
            title='Test Topic',
            description='Test topic for unit tests',
            prompt='Test prompt for AI generation',
            group=self.group,
            created_by=self.admin_user,
            instructional_text='Test instructions',
            content_generated=True
        )
    
    def test_home_page_access(self):
        """Test that authenticated users can access home page"""
        self.client.login(username='student', password='testpass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to Teacher Assistant')
    
    def test_topic_detail_access(self):
        """Test that group members can access topic detail"""
        self.client.login(username='student', password='testpass')
        response = self.client.get(reverse('topic_detail', args=[self.topic.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.title)
    
    def test_topic_access_denied(self):
        """Test that non-group members cannot access topic"""
        other_user = User.objects.create_user(username='other', password='testpass')
        self.client.login(username='other', password='testpass')
        response = self.client.get(reverse('topic_detail', args=[self.topic.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to home
    
    def test_admin_dashboard_access(self):
        """Test that admin users can access dashboard"""
        self.client.login(username='admin', password='testpass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
    
    def test_admin_dashboard_denied(self):
        """Test that non-admin users cannot access dashboard"""
        self.client.login(username='student', password='testpass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_creation(self):
        """Test admin can create users"""
        self.client.login(username='admin', password='testpass')
        response = self.client.post(reverse('create_user'), {
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_group_creation(self):
        """Test admin can create groups"""
        self.client.login(username='admin', password='testpass')
        response = self.client.post(reverse('create_group'), {
            'name': 'New Group',
            'description': 'New test group',
            'members': [self.student_user.id]
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Group.objects.filter(name='New Group').exists())
    
    def test_topic_creation(self):
        """Test admin can create topics"""
        self.client.login(username='admin', password='testpass')
        response = self.client.post(reverse('create_topic'), {
            'title': 'New Topic',
            'description': 'New test topic',
            'prompt': 'New test prompt',
            'group': self.group.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Topic.objects.filter(title='New Topic').exists())
    
    def test_progress_tracking(self):
        """Test that user progress is tracked correctly"""
        progress, created = UserTopicProgress.objects.get_or_create(
            user=self.student_user,
            topic=self.topic
        )
        self.assertTrue(created)
        self.assertEqual(progress.total_attempts, 0)
        self.assertFalse(progress.completed)
    
    def test_attempt_creation(self):
        """Test that attempts are created correctly"""
        from django.utils import timezone
        attempt = Attempt.objects.create(
            user=self.student_user,
            topic=self.topic,
            attempt_number=1,
            canvas_data='test_canvas_data',
            time_spent=300,
            started_at=timezone.now(),
            score=15,
            is_correct=False,
            feedback='Test feedback'
        )
        self.assertEqual(attempt.user, self.student_user)
        self.assertEqual(attempt.topic, self.topic)
        self.assertEqual(attempt.score, 15)
    
    def test_models_str_methods(self):
        """Test string representations of models"""
        self.assertEqual(str(self.group), 'Test Group')
        self.assertEqual(str(self.topic), 'Test Topic (Test Group)')
        
        progress = UserTopicProgress.objects.create(
            user=self.student_user,
            topic=self.topic
        )
        self.assertEqual(str(progress), 'student - Test Topic')


class AIServiceTestCase(TestCase):
    """Test cases for AI service functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass',
            is_staff=True
        )
        
        self.group = Group.objects.create(
            name='Test Group',
            created_by=self.admin_user
        )
        
        self.topic = Topic.objects.create(
            title='Test Topic',
            description='Test description',
            prompt='Test prompt',
            group=self.group,
            created_by=self.admin_user
        )
    
    def test_topic_content_generation_flag(self):
        """Test that topics can be marked as having generated content"""
        self.assertFalse(self.topic.content_generated)
        
        self.topic.content_generated = True
        self.topic.instructional_text = 'Generated instructions'
        self.topic.save()
        
        self.assertTrue(self.topic.content_generated)
        self.assertEqual(self.topic.instructional_text, 'Generated instructions')
    
    def test_ai_generation_log_creation(self):
        """Test that AI generation logs can be created"""
        from .models import AIGenerationLog
        
        log = AIGenerationLog.objects.create(
            generation_type='text',
            prompt='Test prompt',
            response='Test response',
            success=True,
            topic=self.topic
        )
        
        self.assertEqual(log.generation_type, 'text')
        self.assertTrue(log.success)
        self.assertEqual(log.topic, self.topic)