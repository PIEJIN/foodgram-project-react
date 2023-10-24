from rest_framework import serializers
from recipes.models import Tag, Ingredient, IngredientRecipe, Recipe, FavoriteRecipe, Cart, TestModel
from django.contrib.auth import get_user_model
from users.models import Follow
from django.core.files.base import ContentFile
import base64
from rest_framework.relations import SlugRelatedField
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework.serializers import SerializerMethodField
from djoser.serializers import UserSerializer


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        return (
            self.context["request"].user.is_authenticated
            and Follow.objects.filter(
                user=self.context["request"].user, follower=obj
            ).exists()
        )


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.cart.filter(recipe=obj).exists()


class FavoriveRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ['recipe']


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    follower = SlugRelatedField(
        slug_field='username',
        read_only=False,
        queryset=User.objects.all()

    )

    class Meta:
        fields = ('user', 'follower')
        model = Follow

    def validate(self, data):
        follower = data['follower']
        user = self.context['request'].user
        if follower == user:
            raise serializers.ValidationError(
                "User and follower cannot be the same."
            )
        if Follow.objects.filter(follower=follower, user=user).exists():
            raise serializers.ValidationError("This follow already exists.")
        return data


class TestSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)

    class Meta:
        fields = ['author',]
        model = TestModel
