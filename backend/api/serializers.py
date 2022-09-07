from django.contrib.auth import get_user_model, password_validation
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True, validators=(password_validation.validate_password,))

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                obj.followers.filter(id=user.id).exists())

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, required=True,
        validators=(password_validation.validate_password,))
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def create(self, validated_data):
        user = self.context['user']
        password = validated_data['new_password']
        user.set_password(password)
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)
    name = serializers.CharField(read_only=True)
    measurement_unit = serializers.CharField(read_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True)
    image = Base64ImageField(required=True)
    name = serializers.CharField(max_length=200)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        exclude = ('favorited_by', 'author')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Поле обязательно')
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Поле обязательно')
        return value

    def create(self, validated_data):
        validated_data.pop('tags')
        validated_data.pop('ingredients')
        recipe = Recipe(**validated_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        validated_data.pop('tags')
        validated_data.pop('ingredients')
        return super().update(instance, validated_data)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('favorited_by', 'pub_date')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                obj.favorited_by.filter(id=user.id).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                user.shopping_cart.filter(id=obj.id).exists())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for ingredient in data['ingredients']:
            amount = instance.recipeingredients_set.all().get(
                ingredient_id=ingredient['id']).amount
            ingredient['amount'] = amount
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.Serializer):
    author = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_author(self, obj):
        return UserSerializer(obj, context=self.context).data

    def get_recipes(self, obj):
        return RecipeShortSerializer(
            Recipe.objects.filter(author=obj), many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
