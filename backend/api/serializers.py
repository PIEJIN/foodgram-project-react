import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (ImageField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow


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
        request = self.context.get("request")
        if not request.user.is_authenticated or not Follow.objects.filter(
            user=request.user, author=obj
        ).exists():
            return False
        return True


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")

    def validate_amount(self, value):
        print(value)
        if not value.isdigit():
            raise ValidationError(
                "Вес ингредиента должен быть числом."
            )
        if str(value) < 0:
            raise ValidationError(
                "Вес ингредиента не может быть отрицательным."
            )
        return value


class RecipeSerializer(ModelSerializer):
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source="ingredients_recipes", many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated and Favorite.objects.filter(
                user=request.user,
                recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        return (
            request.user.is_authenticated and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj).exists()
        )


class IngredientRecipeCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source="ingredient",
        queryset=Ingredient.objects.all()
    )
    amount = IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeCreateUpdateSerializer(ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField(max_length=None)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",

        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        ingredient_recipe_instances = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredient_recipe_instances)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = super().update(instance, validated_data)
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        ingredient_recipe_instances = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]

        IngredientRecipe.objects.bulk_create(ingredient_recipe_instances)
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context["request"]}
        )
        return serializer.data

    def validate_ingredients(self, values):
        if not values:
            raise ValidationError("Добавьте ингредиенты.")
        unique_ids = set()
        all_ids = []
        for value in values:
            ingredient_id = value['ingredient'].id
            unique_ids.add(ingredient_id)
            all_ids.append(ingredient_id)

            amount = value['amount']
            if not (isinstance(amount, (float, int))):
                raise ValidationError({"amount": "Вес ингредиента должен быть числом"})
            if int(amount) < 0:
                raise ValidationError({"amount": "Вес ингредиента должен быть положительным числом"})

        if len(unique_ids) != len(all_ids):
            raise ValidationError("Одинаковые ингредиенты")

        return values

    def validate_tags(self, values):
        if not values:
            raise ValidationError("Укажите хотя бы 1 тег")

        unique_tags = set(values)
        if len(unique_tags) != len(values):
            raise ValidationError("Дублирование тегов")

        return values

    def validate_name(self, value):
        if Recipe.objects.filter(name=value).exists():
            raise ValidationError("Имя рецепта занято")
        return value


class FollowRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoriteSerializer(ModelSerializer):
    id = ReadOnlyField(source="recipe.id")
    name = ReadOnlyField(source="recipe.name")
    image = ReadOnlyField(source="recipe.image.url")
    cooking_time = ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(ModelSerializer):
    id = ReadOnlyField(source="recipe.id")
    name = ReadOnlyField(source="recipe.name")
    image = ReadOnlyField(source="recipe.image.url")
    cooking_time = ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(ModelSerializer):
    author = ReadOnlyField(source="author.id")
    is_subscribed = SerializerMethodField()
    recipes = FollowRecipeSerializer(source="author.recipes", many=True)

    class Meta:
        model = Follow
        fields = (
            "author",
            "is_subscribed",
            "recipes",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        author = validated_data.get("author")

        if Follow.objects.filter(user=request.user, author=author).exists():
            raise ValidationError({"errors": "Вы уже подписаны"})
        if request.user == author:
            raise ValidationError({"errors": "Самоподписка запрещена"})

        return Follow.objects.create(user=request.user, author=author)

    def destroy(self, instance, validated_data):
        print(validated_data)
        request = self.context.get("request")

        if Follow.objects.filter(
            user=request.user, author=instance.author
        ).exists():
            instance.delete()
        else:
            raise ValidationError(
                {"errors": "У вас нет подписки на этого пользователя"}
            )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        author = instance.author
        data["email"] = author.email
        data["username"] = author.username
        data["first_name"] = author.first_name
        data["last_name"] = author.last_name
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request.user.is_authenticated or not Follow.objects.filter(
            user=request.user, author=obj.author
        ).exists():
            return False
        return True
