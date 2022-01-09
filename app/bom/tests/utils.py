from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile


def _in_memory_file(file_path: str, file_name="file.csv", content_type="text/csv") -> SimpleUploadedFile:
    _file = File(open(file_path))
    encoded_file = _file.read().encode("utf-8")
    file = SimpleUploadedFile(file_name, encoded_file, content_type=content_type)
    return file
