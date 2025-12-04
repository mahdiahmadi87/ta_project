from django.contrib import admin
from .models import Topic

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    filter_horizontal = ('groups',)
    readonly_fields = ('generated_instruction', 'generated_background')
    
    fieldsets = (
        ('Configuration', {
            'fields': ('title', 'description', 'groups', 'prompt')
        }),
        ('AI Generated Assets (Read Only)', {
            'fields': ('generated_background', 'generated_instruction')
        }),
    )