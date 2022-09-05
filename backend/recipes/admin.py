from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    pass


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline,)


class RecipeIngredientsAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline,)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
