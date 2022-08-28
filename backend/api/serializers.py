from rest_framework.serializers import ModelSerializer, SlugRelatedField
from recipes.models import Tag, Ingredient


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
