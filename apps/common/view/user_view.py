from rest_framework.viewsets import ModelViewSet


class UserModelViewSet(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(create_user=self.request.user, update_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(update_user=self.request.user)
