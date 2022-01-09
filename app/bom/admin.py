from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from bom.models import Assembly, Component


class MyAdmin(TreeAdmin):
    form = movenodeform_factory(Assembly)

    list_select_related = (
        'component',
    )


admin.site.register(Assembly, MyAdmin)
admin.site.register(Component)
