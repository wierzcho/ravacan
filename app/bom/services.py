import csv
import io
from typing import Tuple, List, Iterable

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from bom.entities import CSVLineEntity
from bom.models import Component, Assembly


def validated_line(raw_item: List[str]) -> Tuple[CSVLineEntity, List[str]]:
    """ Takes line(row) from csv file and transforms it to CSVLineEntity object.
        Assumes that proper format of file contains following fields in following format:
        level	item_number	item_name	item_category	unit_of_measure	procurement_type	quantity	Price by Unit


        Parameters
        -----------
        raw_item: List[str]
            line(row) from csv file as a raw list of strings

        Returns
        ----------
        CSVLineEntity
            csv text converted to CSVLineEntity object or None if there were any errors
        List
            list of errors if there are any, if not returns empty list
    """
    csv_entity = None
    errors = []

    if len(raw_item) != 8:
        errors.append("Each item should have 8 elements.")
    if not raw_item[0]:
        errors.append("Field required: level")
    if not raw_item[1]:
        errors.append("Field required: identifier")
    if not raw_item[2]:
        errors.append("Field required: name")
    if not raw_item[4]:
        errors.append("Field required: unit")
    if not raw_item[5]:
        errors.append("Field required: procurement_type")
    if not raw_item[6]:
        errors.append("Field required: quantity")

    if not errors:
        csv_entity = CSVLineEntity(depth=int(raw_item[0]),
                                   identifier=raw_item[1],
                                   name=raw_item[2],
                                   category=raw_item[3],
                                   unit=raw_item[4],
                                   procurement_type=raw_item[5],
                                   quantity=float(raw_item[6]),
                                   price=float(raw_item[7]) if raw_item[7] else 0)
    return csv_entity, errors


def _decode_file(file: UploadedFile) -> Iterable:
    """ Decodes file uploaded by user.
        Parameters
        -----------
        file: UploadedFile
            file uploaded by users

        Returns
        ----------
        Iterable
    """
    decoded_file = file.read().decode()
    has_header = csv.Sniffer().has_header(decoded_file)
    io_string = io.StringIO(decoded_file)
    reader = csv.reader(io_string)

    errors = {}
    if has_header:
        next(reader, None)  # skip first row (header)
    else:
        errors['file_structure'] = "File doesn't have header."
    return reader, errors


def validate_file(file: UploadedFile) -> dict:
    """ Validates file

        Parameters
        -----------
        file: UploadedFile
            file uploaded by users

        Returns
        ----------
        Dict
            dict containing validation results

    """
    decoded_file, validation_result = _decode_file(file)

    for idx, row in enumerate(decoded_file):
        entity, errors = validated_line(row)
        if not entity:
            validation_result[f"row_{idx}"] = {
                "row_number": idx,
                "verbose:": errors
            }

    return validation_result


@transaction.atomic
def save_to_db(file: UploadedFile):
    decoded_file, validation_result = _decode_file(file)
    assembly = None

    if validation_result:
        raise Exception("This should already be validated!")

    for idx, row in enumerate(decoded_file):
        entity, errors = validated_line(row)
        if errors:
            raise Exception("This should already be validated!")

        component, _ = Component.objects.get_or_create(identifier=entity.identifier,
                                                       name=entity.name,
                                                       defaults={
                                                           'category': entity.category,
                                                           'unit': entity.unit,
                                                           'procurement_type': entity.procurement_type,
                                                           'price': entity.price,
                                                       })
        entity.depth += 1
        if entity.depth == 1:
            assembly = Assembly.add_root(
                component=component,
                quantity=entity.quantity,
                depth=entity.depth,
            )
        else:
            if assembly.depth == entity.depth:
                assembly = assembly.add_sibling(
                    component=component,
                    quantity=entity.quantity,
                    depth=entity.depth,
                )
            elif (assembly.depth + 1) == entity.depth:
                assembly = assembly.add_child(
                    component=component,
                    quantity=entity.quantity,
                    depth=entity.depth,
                )
            else:
                diff = assembly.depth - entity.depth

                for i in range(diff):
                    assembly = assembly.get_parent()

                assembly = assembly.add_sibling(
                    component=component,
                    quantity=entity.quantity,
                    depth=entity.depth,
                )
