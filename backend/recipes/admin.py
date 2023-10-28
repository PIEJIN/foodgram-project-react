from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    min_num = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorite_count")
    search_fields = ("name", "author__email", "tags")
    list_filter = ("author", "tags")
    inlines = [IngredientRecipeInline, TagRecipeInline]

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorite_count.short_description = "В Избранном у:"


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name",)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe")
    search_fields = ("recipe",)


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ("tag", "recipe")
    search_fields = ("tag", "recipe")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(ShoppingCart)
