from collections import OrderedDict
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from bom.models import Assembly
from bom.tests.test_services import CORRECT_FILE, INCORRECT_FILE1, INCORRECT_FILE2
from bom.tests.utils import _in_memory_file


class TestFileAPI(TestCase):
    def setUp(self) -> None:
        self.correct_file = _in_memory_file(file_path=CORRECT_FILE)
        self.incorrect_file1 = _in_memory_file(file_path=INCORRECT_FILE1)
        self.incorrect_file2 = _in_memory_file(file_path=INCORRECT_FILE2)

    def test_file_validation_successful(self):
        res = self.client.post(reverse("bom:file_validate"), {'file': self.correct_file})

        assembly = Assembly.objects.all()
        self.assertEqual(assembly.count(), 0)
        self.assertEqual(res.data, "Validation successful")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_file_validation_not_successful(self):
        res = self.client.post(reverse("bom:file_validate"), {'file': self.incorrect_file1})
        res1 = self.client.post(reverse("bom:file_validate"), {'file': self.incorrect_file2})

        self.assertEqual(res.data, {'file_structure': "File doesn't have header."})
        self.assertEqual(res1.data, {'row_0': {'row_number': 0, 'verbose:': ['Field required: identifier']},
                                     'row_1': {'row_number': 1, 'verbose:': ['Field required: quantity']},
                                     'row_2': {'row_number': 2, 'verbose:': ['Field required: name']},
                                     'row_4': {'row_number': 4, 'verbose:': ['Field required: level']}})
        assembly = Assembly.objects.all()
        self.assertEqual(assembly.count(), 0)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_upload_successful(self):
        res = self.client.post(reverse('bom:file_upload'), {'file': self.correct_file})

        assembly = Assembly.objects.all()
        self.assertEqual(assembly.count(), 7)
        self.assertEqual(res.data, "Uploaded successfully")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_file_upload_successful_not_successful(self):
        res = self.client.post(reverse("bom:file_validate"), {'file': self.incorrect_file1})
        res1 = self.client.post(reverse("bom:file_validate"), {'file': self.incorrect_file2})

        assembly = Assembly.objects.all()
        self.assertEqual(assembly.count(), 0)
        self.assertEqual(res.data, {'file_structure': "File doesn't have header."})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res1.data, {'row_0': {'row_number': 0, 'verbose:': ['Field required: identifier']},
                                     'row_1': {'row_number': 1, 'verbose:': ['Field required: quantity']},
                                     'row_2': {'row_number': 2, 'verbose:': ['Field required: name']},
                                     'row_4': {'row_number': 4, 'verbose:': ['Field required: level']}})
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_item_details_api_view(self):
        self.client.post(reverse('bom:file_upload'), {'file': self.correct_file})
        res1 = self.client.get(reverse('bom:item_details', kwargs={'id': 1}))
        res2 = self.client.get(reverse('bom:item_details', kwargs={'id': 3}))
        res3 = self.client.get(reverse('bom:item_details', kwargs={'id': 5}))

        self.assertEqual(res1.data, {'total_cost': '1.43200', 'data': {'component': 1, 'quantity': Decimal('1.000')},
                                     'children': [{'data': {'component': 2, 'quantity': Decimal('1.000')}, 'children': [
                                         {'data': {'component': 3, 'quantity': Decimal('1.000')},
                                          'children': [{'data': {'component': 4, 'quantity': Decimal('1.000')}},
                                                       {'data': {'component': 5, 'quantity': Decimal('1.000')}},
                                                       {'data': {'component': 6, 'quantity': Decimal('0.550')}}]},
                                         {'data': {'component': 7, 'quantity': Decimal('1.120')}}]}]})
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data, {'total_cost': '0.76000', 'data': {'component': 3, 'quantity': Decimal('1.000')},
                                     'children': [{'data': {'component': 4, 'quantity': Decimal('1.000')}},
                                                  {'data': {'component': 5, 'quantity': Decimal('1.000')}},
                                                  {'data': {'component': 6, 'quantity': Decimal('0.550')}}]})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.data, {'total_cost': '0.11000', 'data': {'component': 5, 'quantity': Decimal('1.000')}})
        self.assertEqual(res3.status_code, status.HTTP_200_OK)

    def test_get_item_details_api_view(self):
        self.client.post(reverse('bom:file_upload'), {'file': self.correct_file})
        res = self.client.get(reverse('bom:item_list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(res.data[0]), {'id': 1, 'component': OrderedDict(
            [('identifier', '999-0001-00'), ('name', 'headphonesz'), ('category', ''), ('unit', 'EA'),
             ('procurement_type', 'MTS'), ('price', '0.00')]), 'depth': 1, 'quantity': '1.000'})

