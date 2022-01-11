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
                         {'total_cost': '1.43200', 'assembly': {
                             'component': {'identifier': '999-0001-00', 'name': 'headphonesz', 'category': '',
                                           'unit': 'EA', 'procurement_type': 'MTS', 'price': Decimal('0.00')},
                             'quantity': Decimal('1.000')}, 'id': 1, 'children': [{'assembly': {
                             'component': {'identifier': '800-0001-00', 'name': 'Assembled headmount', 'category': '',
                                           'unit': 'EA', 'procurement_type': 'MTS', 'price': Decimal('0.00')},
                             'quantity': Decimal('1.000')}, 'id': 2, 'children': [{'assembly': {
                             'component': {'identifier': '750-0001-01', 'name': 'covered headmount', 'category': '',
                                           'unit': 'EA', 'procurement_type': 'MTS', 'price': Decimal('0.00')},
                             'quantity': Decimal('1.000')}, 'id': 3, 'children': [{'assembly': {
                             'component': {'identifier': '400-0001-00', 'name': 'plastic structure headmount',
                                           'category': '', 'unit': 'EA', 'procurement_type': 'MTS',
                                           'price': Decimal('0.32')}, 'quantity': Decimal('1.000')}, 'id': 4}, {
                                                                                      'assembly': {'component': {
                                                                                          'identifier': '240-0001-00',
                                                                                          'name': 'solid foam',
                                                                                          'category': '', 'unit': 'EA',
                                                                                          'procurement_type': 'MTS',
                                                                                          'price': Decimal('0.11')},
                                                                                                   'quantity': Decimal(
                                                                                                       '1.000')},
                                                                                      'id': 5}, {'assembly': {
                             'component': {'identifier': '230-0001-00', 'name': 'leather rectange', 'category': '',
                                           'unit': 'EA', 'procurement_type': 'MTS', 'price': Decimal('0.60')},
                             'quantity': Decimal('0.550')}, 'id': 6}]}, {'assembly': {
                             'component': {'identifier': '210-0101-00', 'name': 'somethingelse', 'category': '',
                                           'unit': 'EA', 'procurement_type': 'MTS', 'price': Decimal('0.60')},
                             'quantity': Decimal('1.120')}, 'id': 7}]}]}
                         )
