from rest_framework import serializers
from .models import Group, Topic, UserTopicProgress, Attempt


class GroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_at', 'member_count', 'topic_count']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_topic_count(self, obj):
        return obj.topics.count()


class TopicSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'title', 'description', 'group_name', 'content_generated', 'created_at']


class UserTopicProgressSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserTopicProgress
        fields = ['user_name', 'topic_title', 'completed', 'final_score', 'total_attempts', 'total_time_spent']


class AttemptSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    
    class Meta:
        model = Attempt
        fields = ['id', 'user_name', 'topic_title', 'attempt_number', 'score', 'is_correct', 'time_spent', 'submitted_at']


class SubmissionSerializer(serializers.Serializer):
    canvas_data = serializers.CharField()
    time_spent = serializers.IntegerField(min_value=0)