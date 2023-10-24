from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteViewSet, FollowViewSet, IngredientListView,
                    RecipeViewSet, CartViewSet, TagViewSet,
                    SelfUserViewSet)

app_name = "api"

router = routers.DefaultRouter()
router.register("tags", TagViewSet)
router.register("ingredients", IngredientListView)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("recipes/<int:id>/favorite/", FavoriteViewSet.as_view(actions={
        'post': 'create',
        'delete': 'destroy',
    })),
    path("recipes/download_shopping_cart/", CartViewSet.as_view(actions={
        'get': 'retrieve',
    })),
    path("recipes/<int:id>/shopping_cart/", CartViewSet.as_view(actions={
        'post': 'create',
        'delete': 'destroy',
    })),
    path("users/subscriptions/", FollowViewSet.as_view(actions={
        'get': 'list',
    })),
    path("users/me/", SelfUserViewSet.as_view(actions={
        'get': 'retrieve',
    })),
    path("users/<int:id>/subscribe/", FollowViewSet.as_view(actions={
        'post': 'create',
        'delete': 'destroy',
    })),
    path("", include("djoser.urls")),
    path("", include(router.urls)),
]
