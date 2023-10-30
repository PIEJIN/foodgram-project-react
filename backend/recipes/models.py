from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=150, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, through="TagRecipe")
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe"
    )
    name = models.CharField(max_length=150)
    image = models.ImageField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        error_messages={
            'min_value': 'Значение должно быть больше 0.',
        }
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=("name", "author"), name="unique_recipe"
            ),
        )

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name="Тег",
        related_name="tags_recipes",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="tags_recipes",
        on_delete=models.CASCADE,
    )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        related_name="ingredients_recipes",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="ingredients_recipes",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        error_messages={
            'min_value': 'Значение должно быть больше 0.',
        }
    )

    constraints = (
        models.UniqueConstraint(
            fields=["ingredient", "recipe"],
            name="recipe_ingredient_unique"
        ),
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    constraints = (
        models.UniqueConstraint(
            fields=["user", "recipe"], name="favorite_unique"
        ),
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="cart",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="cart",
        on_delete=models.CASCADE,
    )
    constraints = (
        models.UniqueConstraint(
            fields=["user", "recipe"], name="cart_unique"
        ),
    )
