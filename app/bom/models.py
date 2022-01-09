from django.core import serializers
from django.db import models

from treebeard.mp_tree import MP_Node, get_result_class


class Component(models.Model):
    identifier = models.CharField(verbose_name="Identifier", max_length=255)
    name = models.CharField(verbose_name="Name", max_length=255)
    category = models.CharField(verbose_name="Category", max_length=255)
    unit = models.CharField(verbose_name="Unit", max_length=255)
    procurement_type = models.CharField(verbose_name="Procurement type", max_length=255)
    price = models.DecimalField(verbose_name="Price", max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.identifier}, {self.name}"


class Assembly(MP_Node):
    steplen = 10

    component = models.ForeignKey("Component", on_delete=models.CASCADE)
    quantity = models.DecimalField(
        verbose_name="Quantity", max_digits=8, decimal_places=3, default=0.0
    )

    @property
    def price(self) -> float:
        return self.quantity * self.component.price

    def __str__(self) -> str:
        return f"{self.component}"

    class Meta:
        verbose_name = "Assembly"
        verbose_name_plural = "Assemblies"

    @classmethod
    def dump_bulk(cls, parent=None, keep_ids=True):
        """
        METHOD OVERRIDDEN FROM django-treebeard
        Dumps a tree branch to a python data structure, calculates total_cost of item.
        """

        cls = get_result_class(cls)

        qset = cls._get_serializable_model().objects.select_related('component').all()
        if parent:
            qset = qset.filter(path__startswith=parent.path)
        ret, lnk = [], {}
        pk_field = cls._meta.pk.attname

        for pyobj in serializers.serialize('python', qset):
            fields = pyobj['fields']
            path = fields['path']
            depth = int(len(path) / cls.steplen)
            del fields['depth']
            del fields['path']
            del fields['numchild']
            if pk_field in fields:
                del fields[pk_field]

            newobj = {f'data': fields}
            if keep_ids:
                newobj[pk_field] = pyobj['pk']

            if (not parent and depth == 1) or \
                    (parent and len(path) == len(parent.path)):
                ret.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)
                parentobj = lnk[parentpath]
                if 'children' not in parentobj:
                    parentobj['children'] = []
                parentobj['children'].append(newobj)
            lnk[path] = newobj

        total_cost = 0
        for el in qset:
            if not el.depth == 1:
                total_cost += el.price
        total = {'total_cost': str(total_cost)}
        ret = {**total, **ret[0]}

        return ret
