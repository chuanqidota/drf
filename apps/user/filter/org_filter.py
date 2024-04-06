from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters

from user.models import Org


class OrgFilterClass(filters.FilterSet):
    gte_ctime = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte', help_text=_('起始时间'))
    lte_ctime = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte', help_text=_('结束时间'))

    class Meta:
        model = Org
        fields = ['id', 'gte_ctime', 'lte_ctime', 'name']
