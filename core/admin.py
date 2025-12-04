from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Group, Topic, UserTopicProgress, Attempt, AIGenerationLog


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'member_count', 'topic_count', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']
    readonly_fields = ['created_at']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
    
    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = 'Topics'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'created_by', 'content_generated', 'created_at']
    list_filter = ['content_generated', 'created_at', 'group']
    search_fields = ['title', 'description', 'prompt']
    readonly_fields = ['created_at', 'content_generated', 'generation_error']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'group', 'created_by')
        }),
        ('AI Content', {
            'fields': ('prompt', 'background_image', 'instructional_text')
        }),
        ('Generation Status', {
            'fields': ('content_generated', 'generation_error', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_by',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not change:  # creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'completed', 'final_score', 'total_attempts', 'total_time_display']
    list_filter = ['completed', 'topic__group', 'first_attempt_at']
    search_fields = ['user__username', 'topic__title']
    readonly_fields = ['first_attempt_at', 'completed_at']
    
    def total_time_display(self, obj):
        if obj.total_time_spent:
            minutes = obj.total_time_spent // 60
            seconds = obj.total_time_spent % 60
            return f"{minutes}m {seconds}s"
        return "0s"
    total_time_display.short_description = 'Total Time'


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'attempt_number', 'score', 'is_correct', 'time_display', 'submitted_at']
    list_filter = ['is_correct', 'evaluation_completed', 'submitted_at', 'topic__group']
    search_fields = ['user__username', 'topic__title']
    readonly_fields = ['id', 'submitted_at', 'evaluation_completed']
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('user', 'topic', 'attempt_number', 'started_at', 'submitted_at')
        }),
        ('Canvas Data', {
            'fields': ('canvas_data',),
            'classes': ('collapse',)
        }),
        ('Evaluation Results', {
            'fields': ('score', 'is_correct', 'feedback', 'evaluation_completed', 'evaluation_error')
        }),
        ('Updated Content', {
            'fields': ('updated_background_image', 'updated_instructional_text'),
            'classes': ('collapse',)
        }),
    )
    
    def time_display(self, obj):
        if obj.time_spent:
            minutes = obj.time_spent // 60
            seconds = obj.time_spent % 60
            return f"{minutes}m {seconds}s"
        return "0s"
    time_display.short_description = 'Time Spent'


@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display = ['generation_type', 'success', 'topic_link', 'attempt_link', 'created_at']
    list_filter = ['generation_type', 'success', 'created_at']
    search_fields = ['prompt', 'response', 'error_message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Generation Info', {
            'fields': ('generation_type', 'success', 'created_at')
        }),
        ('Content', {
            'fields': ('prompt', 'response', 'error_message')
        }),
        ('Related Objects', {
            'fields': ('topic', 'attempt'),
            'classes': ('collapse',)
        }),
        ('Cost Tracking', {
            'fields': ('api_cost',),
            'classes': ('collapse',)
        }),
    )
    
    def topic_link(self, obj):
        if obj.topic:
            url = reverse('admin:core_topic_change', args=[obj.topic.id])
            return format_html('<a href="{}">{}</a>', url, obj.topic.title)
        return '-'
    topic_link.short_description = 'Topic'
    
    def attempt_link(self, obj):
        if obj.attempt:
            url = reverse('admin:core_attempt_change', args=[obj.attempt.id])
            return format_html('<a href="{}">{}</a>', url, f"Attempt {obj.attempt.attempt_number}")
        return '-'
    attempt_link.short_description = 'Attempt'


# Customize admin site
admin.site.site_header = "Teacher Assistant Admin"
admin.site.site_title = "TA Admin"
admin.site.index_title = "Welcome to Teacher Assistant Administration"