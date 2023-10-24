from django.urls import include, path
from .views import TagGetView, IngredientGetView, RecipeView, RecipeFavoriteView, FollowView, TestView
from rest_framework import routers

app_name = "api"

v1_router = routers.DefaultRouter()


v1_router.register(r'tags', TagGetView)
v1_router.register(r'ingredients', IngredientGetView)
v1_router.register(r'recipes', RecipeView)
v1_router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowView,
    basename='subscribe'
    )
v1_router.register(
    r'users/subscriptions',
    FollowView,
    basename='subscriptions'
)
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    RecipeFavoriteView,
    basename='favorite')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    RecipeFavoriteView,
    basename='shopping_cart')


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
    path('', include(v1_router.urls),),
    
]
