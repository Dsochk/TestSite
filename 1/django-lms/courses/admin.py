from django.contrib import admin
from .models import Course, UserProfile, Enrollment, SavedSearch


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'userprofile', 'is_hidden', 'created_at']
    list_filter = ['category', 'level', 'is_hidden']
    search_fields = ['title', 'description']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'api_key']
    search_fields = ['user__username', 'api_key']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at']
    list_filter = ['enrolled_at']


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'created_at']
    search_fields = ['name', 'user__username']
