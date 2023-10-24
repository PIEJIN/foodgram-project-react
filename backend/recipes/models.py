
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = ('Тег')
        verbose_name_plural = ('Теги')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    amount = models.IntegerField()
    measurement_unit = models.CharField(max_length=200)  # !!!!

    class Meta:
        verbose_name = ('Ингредиент')
        verbose_name_plural = ('Ингредиенты')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author'
    )
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=200, blank=True)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name="recipe_ingredients"
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='tags'
    )
    cooking_time = models.PositiveIntegerField()
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        verbose_name = ('Рецепт')
        verbose_name_plural = ('Рецепты')

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorite')


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cart')


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class TestModel(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)


@receiver(post_save, sender=FavoriteRecipe)
def set_recipe_is_favorited_true(sender, instance, created, **kwargs):
    if created:
        instance.recipe.is_favorited = True
        instance.recipe.save()


@receiver(post_delete, sender=FavoriteRecipe)
def set_recipe_is_favorited_false(sender, instance, **kwargs):
    instance.recipe.is_favorited = False
    instance.recipe.save()


@receiver(post_save, sender=Cart)
def set_recipe_is_in_cart_true(sender, instance, created, **kwargs):
    if created:
        instance.recipe.is_in_shopping_cart = True
        instance.recipe.save()


@receiver(post_delete, sender=Cart)
def set_recipe_is_in_cart_false(sender, instance, **kwargs):
    instance.recipe.is_in_shopping_cart = False
    instance.recipe.save()
