from rest_framework import mixins, viewsets


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """
    Вьюсет определяющий методы POST и DELETE
    """
    pass
