from drf_yasg.inspectors.view import SwaggerAutoSchema
from rest_framework.viewsets import ModelViewSet


class CustomAutoSchema(SwaggerAutoSchema):

    def get_tags(self, operation_keys=None):
        tags = self.overrides.get('tags', None) or getattr(self.view, 'tags', [])
        if not tags:
            tags = [operation_keys[0]]
        return tags

    def get_operation_id(self, operation_keys=None):
        bulk = False
        if isinstance(self.view, ModelViewSet) and 'bulk' in self.view.action:
            bulk = True

        operation_keys = operation_keys or self.operation_keys

        panda_op_id = getattr(self.view, 'operation_id', None)
        if panda_op_id and operation_keys:
            panda_op_id = '%s-%s' % (panda_op_id, operation_keys[-1])
            if bulk:
                panda_op_id = '%s-bulk' % panda_op_id
        operation_id = self.overrides.get('operation_id', '') or panda_op_id
        if not operation_id:
            operation_id = '_'.join(operation_keys)
        return operation_id
