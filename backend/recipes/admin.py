from django.contrib import admin

from .models import Cart, Tag, Recipe, Ingredient, IngredientRecipe, FavoriteRecipe


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1  # Количество дополнительных полей для добавления ингредиентов


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount')
    list_filter = ['name']


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class CartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Cart, CartAdmin)
