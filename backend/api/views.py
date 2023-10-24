from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet
from users.models import Follow, User

from .filters import RecipeFilter
from .permissions import IsAuthorPatchDelete
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientListView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    @classmethod
    def get_extra_actions(cls):
        return []


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorPatchDelete,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = RecipeSerializer(instance, context={"request": request})
        return Response(serializer.data)

    def list(self, request):
        queryset = self.filter_queryset(self.queryset.prefetch_related(
            "ingredients_recipes__ingredient", "tags"
        ))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def create(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        queryset = Favorite.objects.filter(user=request.user, recipe=recipe)
        if queryset.exists():
            return Response(
                {"errors": "Рецепт уже в избранном"},
                status=HTTP_400_BAD_REQUEST,
            )
        instance = Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def destroy(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        queryset = Favorite.objects.filter(user=request.user, recipe=recipe)
        if queryset.exists():
            instance = queryset.first()
            instance.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепт не был в избранном"},
            status=HTTP_400_BAD_REQUEST,
        )


class CartViewSet(ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def create(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        queryset = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
            )
        if queryset.exists():
            return Response(
                {"errors": "Рецепт уже в корзине"},
                status=HTTP_400_BAD_REQUEST,
            )
        instance = ShoppingCart.objects.create(
            user=request.user, recipe=recipe
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def destroy(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        queryset = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
            )
        if queryset.exists():
            instance = queryset.first()
            instance.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепта не было в корзине"},
            status=HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request):
        shopping_cart = {}
        ingredients_recipes = IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        )
        for ingredient_recipe in ingredients_recipes:
            if ingredient_recipe.ingredient.name in shopping_cart:
                shopping_cart[
                    ingredient_recipe.ingredient.name
                    ][1] += ingredient_recipe.amount
            else:
                shopping_cart[ingredient_recipe.ingredient.name] = [
                    ingredient_recipe.ingredient.measurement_unit,
                    ingredient_recipe.amount,
                ]
        content = ""
        for ingredient, values in shopping_cart.items():
            content += f"{ingredient} ({values[0]}) — {values[1]}\n"
        return HttpResponse(content, content_type="text/plain")


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
        )
    def list(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
        )
    def create(self, request, id):
        user = get_object_or_404(User, id=id)
        if Follow.objects.filter(user=request.user, author=user).exists():
            return Response(
                {"errors": "Вы уже подписаны"},
                status=HTTP_400_BAD_REQUEST,
            )
        if request.user == user:
            return Response(
                {"errors": "Самоподписка запрещена"},
                status=HTTP_400_BAD_REQUEST,
            )
        data = Follow.objects.create(user=request.user, author=user)
        serializer = FollowSerializer(data, context={"request": request})
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(
        detail=True, methods=['delete'], permission_classes=[IsAuthenticated]
        )
    def destroy(self, request, id):
        user = get_object_or_404(User, id=id)
        if Follow.objects.filter(user=request.user, author=user).exists():
            Follow.objects.get(user=request.user, author=user).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "У вас нет подписки на этого пользователя"},
            status=HTTP_400_BAD_REQUEST,
        )


class SelfUserViewSet(ViewSet):
    def retrieve(self, request):
        serializer = CustomUserSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data)
