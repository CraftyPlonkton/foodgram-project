from django.contrib import admin

from users.models import Following, User


class UserAdmin(admin.ModelAdmin):
    pass


class FollowingAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Following, FollowingAdmin)
