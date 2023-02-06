from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг', max_length=200, unique=True)
    slug = models.CharField(
        verbose_name='Слаг', max_length=200, unique=True)
    color = models.CharField(
        verbose_name='Цвет', max_length=7,
        null=True, blank=True,
        default='#C71585', unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=900)
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения', max_length=900)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='recipe')
    name = models.CharField(
        verbose_name='Название', max_length=200)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Фотография блюда')
    text = models.TextField(
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientInRecipe',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги')
    cooking_time = models.IntegerField(
        default=1, blank=False,
        verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(fields=['author', 'name'],
                                    name='unique_author_recipename')
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепт')
    amount = models.IntegerField(
        verbose_name='Количество в рецепте')

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт', related_name='favorite')
    recipe_lover = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Добавил в избранное', related_name='favorite')

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class ShoppingCart(models.Model):
    cart_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Владелец списка покупок')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Рецепт')

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
