from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    search_fields = ("name",)
    list_filter = ("author", "tags")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(ShoppingCart)
