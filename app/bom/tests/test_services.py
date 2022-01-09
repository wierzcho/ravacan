import csv
import os
from decimal import Decimal

from django.core.files import File
from django.test import TestCase

from bom.models import Assembly, Component
from bom.services import validated_line, validate_file, save_to_db
from bom.tests.utils import _in_memory_file

CORRECT_FILE = os.path.join(os.path.dirname(__file__), 'files/correct_file.csv')
INCORRECT_FILE1 = os.path.join(os.path.dirname(__file__), 'files/incorrect_file1_without_header.csv')
INCORRECT_FILE2 = os.path.join(os.path.dirname(__file__), 'files/incorrect_file2.csv')


class TestValidateCSV(TestCase):
    def test_validate_line_successful(self):
        proper_line1 = "0,999-0001-00,headphones,,EA,MTS,1,".split(",")
        proper_line2 = "1,800-0001-00,Assembled headmount,,EA,MTS,1,".split(",")
        csv_line_entity1, errors = validated_line(proper_line1)
        csv_line_entity2, errors = validated_line(proper_line2)

        self.assertEqual(csv_line_entity1.depth, 0)
        self.assertEqual(csv_line_entity1.identifier, "999-0001-00")
        self.assertEqual(csv_line_entity1.name, "headphones")
        self.assertEqual(csv_line_entity1.unit, "EA")
        self.assertEqual(csv_line_entity1.quantity, 1)
        self.assertFalse(errors)
        self.assertEqual(csv_line_entity2.depth, 1)
        self.assertEqual(csv_line_entity2.identifier, "800-0001-00")
        self.assertEqual(csv_line_entity2.name, "Assembled headmount")
        self.assertEqual(csv_line_entity2.unit, "EA")
        self.assertEqual(csv_line_entity2.quantity, 1)
        self.assertFalse(errors)

    def test_validate_line_failed(self):
        line_with_error1 = "0,,headphones,,EA,MTS,,".split(",")
        line_with_error2 = "800-0001-00,Assembled headmount,,EA,MTS,1,".split(",")
        csv_line_failed1, errors1 = validated_line(line_with_error1)
        csv_line_failed2, errors2 = validated_line(line_with_error2)

        self.assertFalse(csv_line_failed1)
        self.assertTrue(errors1)
        self.assertIn("Field required: identifier", errors1)
        self.assertIn("Field required: quantity", errors1)

        self.assertFalse(csv_line_failed2)
        self.assertTrue(errors2)
        self.assertIn("Each item should have 8 elements.", errors2)
        self.assertIn("Field required: name", errors2)
        self.assertIn("Field required: quantity", errors2)

    def test_validate_file_structure_successful(self):
        file = _in_memory_file(file_path=CORRECT_FILE)

        results = validate_file(file)

        self.assertFalse(results)

    def test_detect_lack_of_header_in_file(self):
        file = _in_memory_file(file_path=INCORRECT_FILE1)

        results = validate_file(file)
        self.assertTrue(results)
        self.assertEqual(results['file_structure'], "File doesn't have header.")

    def test_detect_lack_of_required_fields_in_row(self):
        file = _in_memory_file(file_path=INCORRECT_FILE2)

        results = validate_file(file)

        self.assertTrue(results)
        self.assertEqual(results['row_0'], {'row_number': 0, 'verbose:': ['Field required: identifier']})
        self.assertEqual(results['row_1'], {'row_number': 1, 'verbose:': ['Field required: quantity']})
        self.assertEqual(results['row_2'], {'row_number': 2, 'verbose:': ['Field required: name']})
        self.assertEqual(results['row_4'], {'row_number': 4, 'verbose:': ['Field required: level']})

    def test_save_assemblies_to_db(self):
        _file = File(open(CORRECT_FILE))
        file = _in_memory_file(file_path=CORRECT_FILE)

        save_to_db(file)

        assemblies = Assembly.objects.all()
        components = Component.objects.all()
        self.assertEqual(assemblies.count(), 7)
        self.assertEqual(components.count(), 7)

        to_csv = csv.reader(_file)
        next(to_csv)
        for assembly, com, row in zip(assemblies, components, to_csv):
            self.assertEqual(com.identifier, row[1])
            self.assertEqual(com.name, row[2])
            self.assertEqual(com.category, row[3])
            self.assertEqual(com.unit, row[4])
            self.assertEqual(com.procurement_type, row[5])
            self.assertEqual(com.price, Decimal(row[7]) if row[7] else 0)

            self.assertEqual(assembly.component, com)
            self.assertEqual(assembly.depth, int(row[0]) + 1)
            self.assertEqual(assembly.quantity, Decimal(row[6]))

    def test_dont_save_entities_to_db(self):
        file1 = _in_memory_file(file_path=INCORRECT_FILE1)
        file2 = _in_memory_file(file_path=INCORRECT_FILE2)

        with self.assertRaises(Exception):
            save_to_db(file1)
        with self.assertRaises(Exception):
            save_to_db(file2)

        assemblies = Assembly.objects.count()
        components = Component.objects.count()
        self.assertEqual(assemblies, 0)
        self.assertEqual(components, 0)
