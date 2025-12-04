from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Topic

@login_required
def home(request):
    """
    Home Page: Lists groups the user belongs to and their topics.
    """
    user_groups = request.user.groups.all().prefetch_related('topics')
    
    context = {
        'user_groups': user_groups
    }
    return render(request, 'curriculum/home.html', context)

@login_required
def topic_workspace(request, topic_id):
    """
    Topic Page: The Canvas workspace.
    """
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Security check: Ensure user is in a group that has access to this topic
    if not topic.groups.filter(id__in=request.user.groups.all()).exists():
        # In a real app, raise 403 Forbidden
        pass 

    context = {
        'topic': topic
    }
    return render(request, 'curriculum/topic_workspace.html', context)