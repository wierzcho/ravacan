from decimal import Decimal

from django.test import TestCase

from bom.models import Assembly
from bom.services import save_to_db
from bom.tests.test_services import CORRECT_FILE
from bom.tests.utils import _in_memory_file


class TestAssemblyModel(TestCase):
    def setUp(self) -> None:
        self.file = _in_memory_file(file_path=CORRECT_FILE)
        save_to_db(self.file)
        self.assemblies = Assembly.objects.all()

    def test_price_correctly_calculated(self):
        prices = [0, 0, 0, 0.32, 0.11, 0.33, 0.672]
        for assembly, price in zip(self.assemblies, prices):
            self.assertEqual(assembly.price, round(Decimal(price), 5))

    def test_dump_bulk_correctly_renders_assembly_tree(self):
        self.assertEqual(Assembly.dump_bulk(self.assemblies.first()),
                         {'total_cost': '1.43200', 'data': {'component': 1, 'quantity': Decimal('1.000')}, 'id': 1,
                          'children': [{'data': {'component': 2, 'quantity': Decimal('1.000')}, 'id': 2, 'children': [
                              {'data': {'component': 3, 'quantity': Decimal('1.000')}, 'id': 3,
                               'children': [{'data': {'component': 4, 'quantity': Decimal('1.000')}, 'id': 4},
                                            {'data': {'component': 5, 'quantity': Decimal('1.000')}, 'id': 5},
                                            {'data': {'component': 6, 'quantity': Decimal('0.550')}, 'id': 6}]},
                              {'data': {'component': 7, 'quantity': Decimal('1.120')}, 'id': 7}]}]})
