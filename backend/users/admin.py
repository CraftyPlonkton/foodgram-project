from django.contrib import admin
from users.models import Following, User


class FollowingAdminInLine(admin.TabularInline):
    model = Following
    fk_name = 'subscriber'
    extra = 1


class UserAdmin(admin.ModelAdmin):
    inlines = (FollowingAdminInLine, )
    list_display = ('username', 'email', 'last_name', 'first_name', 'is_staff')
    list_filter = ('first_name', 'email')
    search_fields = ('email',)


admin.site.register(User, UserAdmin)
