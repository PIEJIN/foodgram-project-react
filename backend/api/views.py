from rest_framework import generics
from recipes.models import Tag, IngredientRecipe, Ingredient, Recipe, FavoriteRecipe, TestModel
from users.models import Follow
from .serializers import TagSerializer, RecipeReadSerializer, RecipeWriteSerializer, IngredientSerializer, RecipeSerializer, FavoriveRecipeSerializer, FollowSerializer, CustomUserSerializer, TestSerializer
from rest_framework import viewsets
from .mixins import CreateListDestroyUpdateRetrieveViewSetMixin, CreateDestroyViewSetMixin, CreateListDestroyViewSetMixin
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import permissions
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db import models
from collections import defaultdict
from django.db.models.aggregates import Sum
from .permissions import IsAuthorOrReadOnly
from rest_framework.permissions import SAFE_METHODS


from recipes.models import Cart


class TestView(CreateListDestroyUpdateRetrieveViewSetMixin):
    queryset = TestModel.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserView(ViewSet):
    """Вьюсет для работы с текущим пользователем."""

    def retrieve(self, request):
        serializer = CustomUserSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data)


class TagGetView(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientGetView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeView(CreateListDestroyUpdateRetrieveViewSetMixin):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def download_shopping_cart(self, request):
        text_lines = ['Список покупок\n']
        for item in IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ):
            text_lines.append(
                '\t{name}, {measurement_unit}: {total}'.format(
                    name=item['ingredient__name'],
                    measurement_unit=item['ingredient__measurement_unit'],
                    total=item['total_amount']
                )
            )
        response_content = '\n'.join(text_lines)
        response = HttpResponse(
            response_content, content_type='text/plain; charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            'shopping_cart.txt'
            )
        return response


class RecipeFavoriteView(CreateDestroyViewSetMixin):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriveRecipeSerializer

    def perform_create(self, serializer):
        FavoriteRecipe.recipe.is_favorited = True
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        favorite = get_object_or_404(FavoriteRecipe, user=self.request.user, recipe=self.kwargs.get('recipe_id'))
        favorite.delete()


class FollowView(CreateListDestroyViewSetMixin):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
