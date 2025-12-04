from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import base64
from .models import Group, Topic, UserTopicProgress, Attempt
from .services import TopicContentGenerator, AIService, FeedbackGenerator
import logging

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


@login_required
def home(request):
    """Home page showing user's groups and topics"""
    user_groups = request.user.ta_groups.all()
    
    # Get topics for each group with progress
    groups_data = []
    for group in user_groups:
        topics = group.topics.filter(content_generated=True)
        topics_with_progress = []
        
        for topic in topics:
            progress, created = UserTopicProgress.objects.get_or_create(
                user=request.user,
                topic=topic
            )
            topics_with_progress.append({
                'topic': topic,
                'progress': progress
            })
        
        groups_data.append({
            'group': group,
            'topics': topics_with_progress
        })
    
    return render(request, 'core/home.html', {
        'groups_data': groups_data
    })


@login_required
def topic_detail(request, topic_id):
    """Topic page with interactive canvas"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Check if user has access to this topic
    if not request.user.ta_groups.filter(id=topic.group.id).exists():
        messages.error(request, "You don't have access to this topic.")
        return redirect('home')
    
    # Get or create progress
    progress, created = UserTopicProgress.objects.get_or_create(
        user=request.user,
        topic=topic
    )
    
    # Get latest attempt for this user/topic
    latest_attempt = Attempt.objects.filter(
        user=request.user,
        topic=topic
    ).order_by('-attempt_number').first()
    
    # Determine what content to show
    background_image_url = topic.background_image.url if topic.background_image else None
    instructional_text = topic.instructional_text
    
    if latest_attempt and not latest_attempt.is_correct:
        # Show updated content from latest incorrect attempt
        if latest_attempt.updated_background_image:
            background_image_url = latest_attempt.updated_background_image.url
        if latest_attempt.updated_instructional_text:
            instructional_text = latest_attempt.updated_instructional_text
    
    return render(request, 'core/topic_detail.html', {
        'topic': topic,
        'progress': progress,
        'latest_attempt': latest_attempt,
        'background_image_url': background_image_url,
        'instructional_text': instructional_text,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_drawing(request, topic_id):
    """API endpoint for submitting canvas drawings"""
    try:
        topic = get_object_or_404(Topic, id=topic_id)
        
        # Check access
        if not request.user.ta_groups.filter(id=topic.group.id).exists():
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        canvas_data = data.get('canvas_data')
        time_spent = data.get('time_spent', 0)
        
        if not canvas_data:
            return Response({'error': 'Canvas data required'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Get or create progress
            progress, created = UserTopicProgress.objects.get_or_create(
                user=request.user,
                topic=topic
            )
            
            if created or not progress.first_attempt_at:
                progress.first_attempt_at = timezone.now()
            
            # Create new attempt
            attempt_number = progress.total_attempts + 1
            attempt = Attempt.objects.create(
                user=request.user,
                topic=topic,
                attempt_number=attempt_number,
                canvas_data=canvas_data,
                time_spent=time_spent,
                started_at=timezone.now() - timezone.timedelta(seconds=time_spent)
            )
            
            # Update progress
            progress.total_attempts += 1
            progress.total_time_spent += time_spent
            progress.save()
            
            # Evaluate drawing asynchronously (in a real app, use Celery)
            try:
                evaluation_result = AIService.evaluate_drawing(
                    canvas_data=canvas_data,
                    topic_prompt=topic.prompt,
                    instructional_text=topic.instructional_text,
                    background_description=f"Background image for topic: {topic.title}",
                    attempt=attempt
                )
                
                # Update attempt with evaluation
                attempt.score = evaluation_result.get('score', 0)
                attempt.is_correct = evaluation_result.get('is_correct', False)
                attempt.feedback = evaluation_result.get('feedback', '')
                attempt.evaluation_completed = True
                
                if attempt.is_correct:
                    # Mark topic as completed
                    progress.completed = True
                    progress.final_score = attempt.score
                    progress.completed_at = timezone.now()
                    progress.save()
                    
                    response_data = {
                        'success': True,
                        'is_correct': True,
                        'message': 'Everything is correct!',
                        'score': attempt.score,
                        'completed': True
                    }
                else:
                    # Generate corrected content
                    FeedbackGenerator.generate_corrected_content(attempt, evaluation_result)
                    
                    response_data = {
                        'success': True,
                        'is_correct': False,
                        'feedback': attempt.feedback,
                        'score': attempt.score,
                        'updated_background': attempt.updated_background_image.url if attempt.updated_background_image else None,
                        'updated_instructions': attempt.updated_instructional_text,
                        'completed': False
                    }
                
                attempt.save()
                return Response(response_data)
                
            except Exception as e:
                attempt.evaluation_error = str(e)
                attempt.save()
                logger.error(f"Evaluation failed for attempt {attempt.id}: {str(e)}")
                
                return Response({
                    'success': False,
                    'error': 'Evaluation failed. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Submit drawing error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Submission failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard for monitoring groups and progress"""
    groups = Group.objects.all().prefetch_related('members', 'topics')
    
    # Pagination
    paginator = Paginator(groups, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_users = User.objects.count()
    total_topics = Topic.objects.count()
    
    return render(request, 'core/admin_dashboard.html', {
        'page_obj': page_obj,
        'total_users': total_users,
        'total_topics': total_topics,
    })


@user_passes_test(is_admin)
def group_detail_admin(request, group_id):
    """Detailed view of group progress for admins"""
    group = get_object_or_404(Group, id=group_id)
    
    # Get all progress data for this group
    progress_data = []
    for member in group.members.all():
        member_data = {
            'user': member,
            'topics': []
        }
        
        for topic in group.topics.all():
            try:
                progress = UserTopicProgress.objects.get(user=member, topic=topic)
                attempts = Attempt.objects.filter(user=member, topic=topic).order_by('attempt_number')
                
                member_data['topics'].append({
                    'topic': topic,
                    'progress': progress,
                    'attempts': attempts
                })
            except UserTopicProgress.DoesNotExist:
                member_data['topics'].append({
                    'topic': topic,
                    'progress': None,
                    'attempts': []
                })
        
        progress_data.append(member_data)
    
    return render(request, 'core/group_detail_admin.html', {
        'group': group,
        'progress_data': progress_data
    })


@user_passes_test(is_admin)
def create_user(request):
    """Create new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, f'User {username} created successfully')
            return redirect('admin_dashboard')
    
    return render(request, 'core/create_user.html')


@user_passes_test(is_admin)
def create_group(request):
    """Create new group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        member_ids = request.POST.getlist('members')
        
        group = Group.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        
        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            group.members.set(members)
        
        messages.success(request, f'Group {name} created successfully')
        return redirect('admin_dashboard')
    
    users = User.objects.all()
    return render(request, 'core/create_group.html', {'users': users})


@user_passes_test(is_admin)
def create_topic(request):
    """Create new topic with AI content generation"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        prompt = request.POST.get('prompt')
        group_id = request.POST.get('group')
        
        group = get_object_or_404(Group, id=group_id)
        
        topic = Topic.objects.create(
            title=title,
            description=description,
            prompt=prompt,
            group=group,
            created_by=request.user
        )
        
        # Generate AI content
        success = TopicContentGenerator.generate_topic_content(topic)
        
        if success:
            messages.success(request, f'Topic {title} created successfully with AI content')
        else:
            messages.warning(request, f'Topic {title} created but AI content generation failed')
        
        return redirect('admin_dashboard')
    
    groups = Group.objects.all()
    return render(request, 'core/create_topic.html', {'groups': groups})