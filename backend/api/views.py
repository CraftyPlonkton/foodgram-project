import csv

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet, mixins)
from recipes.models import Ingredient, RecipeIngredients, Recipe, Tag

from .filters import RecipeFilter
from .permissions import ListPostAllowAny, OwnerOrReadOnly
from .serializers import (FollowingSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeShortSerializer,
                          RecipeWriteSerializer, SetPasswordSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, GenericViewSet):
    """Получение и создание пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ListPostAllowAny,)

    def perform_create(self, serializer):
        password = serializer.validated_data.pop('password')
        user = serializer.save()
        user.set_password(password)
        user.save()

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Получение информации о себе"""
        user = request.user
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=('post',),
            permission_classes=(IsAuthenticated,),
            serializer_class=SetPasswordSerializer)
    def set_password(self, request):
        """Изменение пароля"""
        user = request.user
        serializer = self.get_serializer(data=request.data,
                                         context={'user': user})
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,),
            serializer_class=SubscriptionSerializer,)
    def subscriptions(self, request):
        """Получение списка подписок на авторов"""
        recipes_limit = self.request.GET.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
        subscriptions = request.user.following.all()
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(
            page, many=True,
            context={'request': request, 'recipes_limit': recipes_limit})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,),
            serializer_class=FollowingSerializer,)
    def subscribe(self, request, pk):
        """Добавление и удаление подписок на авторов"""
        if request.method == 'POST':
            author = get_object_or_404(User, id=pk)
            user = request.user
            serializer = self.get_serializer(
                data={'author': author.id, 'subscriber': user.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = SubscriptionSerializer(author,
                                              context={'request': request})
            return Response(response.data)
        if request.method == 'DELETE':
            author = get_object_or_404(User, id=pk)
            user = request.user
            user.following.remove(author)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(ReadOnlyModelViewSet):
    """Получение информации о тегах"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Получение информации об ингредиентах"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """Получение и создание рецептов"""
    queryset = (Recipe.objects.
                prefetch_related('ingredients', 'tags').
                select_related('author'))
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOrReadOnly)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def add_ingredients_in_recipe(ingredients_data, recipe):
        recipe.ingredients.clear()
        objects = [RecipeIngredients(
            recipe=recipe,
            ingredient=data['id'],
            amount=data['amount']) for data in ingredients_data]
        RecipeIngredients.objects.bulk_create(objects)

    @staticmethod
    def add_tags_in_recipe(tags_data, recipe):
        recipe.tags.clear()
        tags = [tag.id for tag in tags_data]
        recipe.tags.add(*tags)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ingredients_data = serializer.validated_data.pop('ingredients')
        tags_data = serializer.validated_data.pop('tags')
        recipe = serializer.save(author=self.request.user)
        self.add_ingredients_in_recipe(ingredients_data, recipe)
        self.add_tags_in_recipe(tags_data, recipe)
        response = RecipeReadSerializer(
            recipe, context={'request': self.request})
        headers = self.get_success_headers(response.data)
        return Response(
            response.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        ingredients_data = serializer.validated_data.pop('ingredients')
        tags_data = serializer.validated_data.pop('tags')
        recipe = serializer.save(author=self.request.user)
        self.add_ingredients_in_recipe(ingredients_data, recipe)
        self.add_tags_in_recipe(tags_data, recipe)
        response = RecipeReadSerializer(recipe,
                                        context={'request': self.request})
        headers = self.get_success_headers(response.data)
        return Response(
            response.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецептов из списка покупок"""
        if request.method == 'POST':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            user.shopping_cart.add(recipe)
            response = RecipeShortSerializer(recipe)
            return Response(response.data)
        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в формате CSV"""
        ingredients = (
            request.user.shopping_cart.all().
            values_list('recipeingredients__ingredient__name',
                        'recipeingredients__ingredient__measurement_unit'
                        ).annotate(total=Sum('recipeingredients__amount')))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.csv"')
        writer = csv.DictWriter(
            response, fieldnames=['Название', 'единица', 'количество'])
        writer.writeheader()
        for ingredient in ingredients:
            row = dict(zip(writer.fieldnames, ingredient))
            writer.writerow(row)
        return response

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавление у удаление рецептов из избранного"""
        if request.method == 'POST':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            recipe.favorited_by.add(user)
            response = RecipeShortSerializer(recipe)
            return Response(response.data)
        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            recipe.favorited_by.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
