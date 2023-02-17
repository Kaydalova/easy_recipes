from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import CreateDestroyViewSet
from .paginators import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для просмотра списка или одного рецепта (доступно всем),
    создания (доступно авторизованным),
    изменения или удаления автором его рецепта.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    """
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Для тэгов нужны только list() и retrieve() методы.
    Доступен для чтения всем, изменять можно только через админку.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    По аналогии с тэгами ингридиенты можно только читать
    (получить весь list или каждый по id).
    Добавление в список ингридиентов доступно только через админку.
    QUERY PARAMETERS: name.
    Поиск по частичному вхождению в начале названия ингредиента.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """
    Вьюесет позволяет посмотреть список подписок.
    Переопределяем queryset так как в сериализаторе используем
    dotted notation и лучше prefetch_related объекты author.
    """
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return Subscribe.objects.filter(
            user=self.request.user).prefetch_related('author')


class SubscribeAPIView(APIView):
    """
    Класс для создания и удаления подписок
    """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscribe.objects.filter(
            author=author, user=request.user)
        if subscription.exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        queryset = Subscribe.objects.create(author=author, user=request.user)
        serializer = SubscribeSerializer(
            queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        subscription = Subscribe.objects.filter(
            author=author, user=user)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы еще не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'recipe': self.kwargs.get('recipe_id')})
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(
            recipe_lover=self.request.user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        recipe = self.kwargs.get('recipe_id')
        recipe_lover = self.request.user
        if not Favorite.objects.filter(recipe=recipe,
                                       recipe_lover=recipe_lover).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Favorite,
            recipe_lover=recipe_lover,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    """
    Вьюсет позволяет добавлять и удалять рецепты из корзины покупок
    """
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        """
        Метод передает в сериализатор необходимые ему для создания модели
        атрибуты cart_owner и recipe.
        """
        context = super().get_serializer_context()
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        context.update({'recipe': recipe})
        context.update({'cart_owner': self.request.user})
        return context

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        recipe = self.kwargs.get('recipe_id')
        cart_owner = self.request.user
        if not ShoppingCart.objects.filter(recipe=recipe,
                                           cart_owner=cart_owner).exists():
            return Response({'errors': 'Рецепт не добавлен в список покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            ShoppingCart,
            cart_owner=cart_owner,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        if not ShoppingCart.objects.filter(cart_owner=request.user).exists():
            return Response({'errors': 'В вашем списке покупок ничего нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        rec_pk = ShoppingCart.objects.filter(
            cart_owner=request.user).values('recipe_id')
        ingredients = IngredientInRecipe.objects.filter(
            recipe_id__in=rec_pk).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount')).order_by()

        text = 'Список покупок:\n\n'
        for item in ingredients:
            text += (f'{item["ingredient__name"]}: '
                     f'{item["amount"]} '
                     f'{item["ingredient__measurement_unit"]}\n')

        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
