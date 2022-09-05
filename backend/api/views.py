from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet, mixins)

from recipes.models import Ingredient, Recipe, Tag, User

from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, SetPasswordSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        user = request.user
        serializer = SetPasswordSerializer(
            data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,),
            queryset=Recipe.objects.all())
    def subscriptions(self, request):
        subscriptions = request.user.following.all()
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        if request.method == 'POST':
            author = self.get_object()
            user = request.user
            user.following.add(author)
            serializer = SubscriptionSerializer(author)
            return Response(serializer.data)
        if request.method == 'DELETE':
            author = self.get_object()
            user = request.user
            user.following.remove(author)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = (Recipe.objects.
                prefetch_related('ingredients', 'tags').
                select_related('author'))
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            user = request.user
            recipe = self.get_object()
            user.shopping_cart.add(recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data)
        if request.method == 'DELETE':
            user = request.user
            recipe = self.get_object()
            user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=('get',))
    def download_shopping_cart(self, request):
        ingredients = (
            request.user.shopping_cart.all().
            values_list('recipeingredients__ingredient__name',
                        'recipeingredients__ingredient__measurement_unit').
            annotate(total=Sum('recipeingredients__amount')))
        # TODO response to pdf
        return Response(data='ffff')

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk):
        if request.method == 'POST':
            user = request.user
            recipe = self.get_object()
            recipe.favorited_by.add(user)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data)
        if request.method == 'DELETE':
            user = request.user
            recipe = self.get_object()
            recipe.favorited_by.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
