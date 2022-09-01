from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from recipes.models import Tag, Ingredient, Recipe

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    measurement_unit = SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'
