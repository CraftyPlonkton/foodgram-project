from django.contrib import admin

from users.models import Following, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_name', 'first_name', 'is_staff')
    list_filter = ('first_name', 'email')
    search_fields = ('email',)


class FollowingAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Following, FollowingAdmin)
