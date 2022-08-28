from django.contrib import admin

from recipes.models import Tag, Ingredient


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
