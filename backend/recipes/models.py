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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(max_length=150)

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
    text = models.CharField(max_length=150)
    cooking_time = models.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        verbose_name = "Рецепт"
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
        related_name="ingredients_recipes",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredients_recipes",
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(validators=(MinValueValidator(1),))


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
