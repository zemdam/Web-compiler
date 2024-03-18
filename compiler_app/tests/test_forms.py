from django.test import TestCase
from ..forms import (
    NewCatalogForm,
    AddSectionForm,
    UploadFileForm,
    StandardForm,
    OptimizationsForm,
    ProcessorForm,
    OptionsMCS51Form,
    OptionsSTM8Form,
    OptionsZ80Form,
)
from ..models import User, File, SectionType
from django.core.files.uploadedfile import SimpleUploadedFile


def create_file():
    user = User.objects.create()
    uploaded_file = SimpleUploadedFile("name.c", b"data")
    file = File.objects.create(
        name="Sample name", owner=user, actual_file=uploaded_file
    )

    return file


def create_section_type():
    section_type = SectionType.objects.create(
        name="Sample name", type="Sample type", css_class="Sample class"
    )

    return section_type


class TestForms(TestCase):
    def test_valid_new_catalog_form(self):
        form = NewCatalogForm(data={"name": "CorrectName"})
        self.assertTrue(form.is_valid())

    def test_invalid_new_catalog_form(self):
        invalid_name = "s" * 40
        form = NewCatalogForm(data={"name": invalid_name})
        self.assertFalse(form.is_valid())


def get_valid_add_section_data():
    data = {
        "section_start": 1,
        "section_end": 1,
        "section_type": create_section_type(),
        "section_of": create_file(),
    }
    return data


class TestAddSectionForm(TestCase):
    def test_valid_data(self):
        data = get_valid_add_section_data()
        form = AddSectionForm(data=data)
        self.assertTrue(form.is_valid())

    def test_negative_number(self):
        data = get_valid_add_section_data()
        data["section_start"] = -1
        form = AddSectionForm(data=data)
        self.assertFalse(form.is_valid())

    def test_no_file(self):
        data = get_valid_add_section_data()
        data["section_of"] = 124
        form = AddSectionForm(data=data)
        self.assertFalse(form.is_valid())

    def test_no_numbers(self):
        data = get_valid_add_section_data()
        data["section_start"] = None
        data["section_end"] = None
        form = AddSectionForm(data=data)
        self.assertFalse(form.is_valid())

    def test_text_instead_of_numbers(self):
        data = get_valid_add_section_data()
        data["section_start"] = "Text"
        form = AddSectionForm(data=data)
        self.assertFalse(form.is_valid())


class TestUploadFileForm(TestCase):
    def test_valid_data(self):
        file = SimpleUploadedFile("name.c", b"data")
        form = UploadFileForm(files={"actual_file": file})
        self.assertTrue(form.is_valid())

    def test_wrong_extension(self):
        file = SimpleUploadedFile("name.d", b"data")
        form = UploadFileForm(files={"actual_file": file})
        self.assertFalse(form.is_valid())

    def test_no_file(self):
        form = UploadFileForm()
        self.assertFalse(form.is_valid())


class TestStandardForm(TestCase):
    def test_valid_data(self):
        form = StandardForm(data={"standard": "--std-c89"})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = StandardForm(data={"standard": "invalid data"})
        self.assertFalse(form.is_valid())


class TestOptimizationsForm(TestCase):
    def test_valid_data(self):
        form = OptimizationsForm(data={"optimizations": ["--nogcse", "--noinduction"]})
        self.assertTrue(form.is_valid())
        form = OptimizationsForm(data={"optimizations": []})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = OptimizationsForm(
            data={"optimizations": ["invalid data", "--noinduction"]}
        )
        self.assertFalse(form.is_valid())
        form = OptimizationsForm(data={"optimizations": "invalid data"})
        self.assertFalse(form.is_valid())


class TestProcessorForm(TestCase):
    def test_valid_data(self):
        form = ProcessorForm(data={"processor": "-mz80"})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = ProcessorForm(data={"processor": "invalid data"})
        self.assertFalse(form.is_valid())


class TestOptionsMCS51Form(TestCase):
    def test_valid_data(self):
        form = OptionsMCS51Form(data={"proc_option1": "--model-small"})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = OptionsMCS51Form(data={"proc_option1": "invalid data"})
        self.assertFalse(form.is_valid())


class TestOptionsZ80Form(TestCase):
    def test_valid_data(self):
        form = OptionsZ80Form(
            data={"proc_option1": ["--emit-externs", "--callee-saves-bc"]}
        )
        self.assertTrue(form.is_valid())
        form = OptionsZ80Form(data={"proc_option1": []})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = OptionsZ80Form(data={"proc_option1": ["invalid data", "--noinduction"]})
        self.assertFalse(form.is_valid())
        form = OptionsZ80Form(data={"proc_option1": "invalid data"})
        self.assertFalse(form.is_valid())


class TestOptionsSTM8Form(TestCase):
    def test_valid_data(self):
        form = OptionsSTM8Form(
            data={"proc_option1": "--model-medium", "proc_option2": ["--out-fmt-elf"]}
        )
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = OptionsSTM8Form(data={"proc_option1": "invalid data"})
        self.assertFalse(form.is_valid())
