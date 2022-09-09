from django.contrib import admin
from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )
    search_fields = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline,)
    list_display = ('name', 'author', 'pub_date', 'favorites_count')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    ordering = ('-pub_date',)
    filter_horizontal = ('favorited_by',)

    def favorites_count(self, obj):
        return obj.favorited_by.all().count()

    favorites_count.__name__ = 'Добавлений в избранное'


class RecipeIngredientsAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline,)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
