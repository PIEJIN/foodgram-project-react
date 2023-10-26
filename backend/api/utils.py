from django.http import HttpResponse


def text_response(ingredients_recipes, shopping_cart={}):
    for ingredient_recipe in ingredients_recipes:
        if ingredient_recipe.ingredient.name in shopping_cart:
            shopping_cart[
                ingredient_recipe.ingredient.name
            ][1] += ingredient_recipe.amount
        else:
            shopping_cart[ingredient_recipe.ingredient.name] = [
                ingredient_recipe.ingredient.measurement_unit,
                ingredient_recipe.amount,
            ]
    content = ""
    for ingredient, values in shopping_cart.items():
        content += f"{ingredient} ({values[0]}) — {values[1]}\n"
    return HttpResponse(content, content_type="text/plain")
