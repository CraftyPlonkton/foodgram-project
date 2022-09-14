from django_filters.rest_framework import (FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    author = NumberFilter(field_name='author__id')
    is_favorited = NumberFilter(method='get_favorite_recipes')
    is_in_shopping_cart = NumberFilter(method='get_shopping_cart')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')

    def get_favorite_recipes(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_by__id=user.id)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__id=user.id)
        return queryset
