from django.test import TestCase
from ..models import Catalog, User, File, SectionType, SectionStatus, FileSection
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile


class TestCatalog(TestCase):
    def test_valid_creation(self):
        user = User.objects.create()
        catalog = Catalog.objects.create(name="Sample name", owner=user)
        self.assertTrue(isinstance(catalog, Catalog))

    def test_no_args(self):
        self.assertRaises(IntegrityError, Catalog.objects.create)

    def test_only_name(self):
        self.assertRaises(IntegrityError, Catalog.objects.create, name="Sample name")


class TestFile(TestCase):
    def test_valid_creation(self):
        user = User.objects.create()
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        file = File.objects.create(
            name="Sample file name", owner=user, actual_file=uploaded_file
        )
        self.assertTrue(isinstance(file, File))

    def test_no_args(self):
        self.assertRaises(IntegrityError, File.objects.create)

    def test_only_name(self):
        self.assertRaises(IntegrityError, File.objects.create, name="Sample file name")


class TestSectionType(TestCase):
    def test_valid_creation(self):
        section_type = SectionType.objects.create(
            name="Sample name", type="Sample type", css_class="Sample class"
        )
        self.assertTrue(isinstance(section_type, SectionType))

    def test_unique_type(self):
        section_type = SectionType.objects.create(
            name="Sample name", type="Sample type", css_class="Sample class"
        )
        self.assertRaises(
            IntegrityError,
            SectionType.objects.create,
            name="Sample name2",
            type="Sample type",
            css_class="Sample class2",
        )

    def test_blank_name(self):
        section_type = SectionType.objects.create(
            type="Sample type", css_class="Sample class"
        )
        self.assertTrue(isinstance(section_type, SectionType))


class TestSectionStatus(TestCase):
    def test_valid_creation(self):
        section_status = SectionStatus.objects.create(status="Sample status")
        self.assertTrue(isinstance(section_status, SectionStatus))

    def test_no_status(self):
        self.assertRaises(IntegrityError, SectionStatus.objects.create, status=None)


class TestFileSection(TestCase):
    def test_valid_creation(self):
        file = File.objects.create(name="Sample name", owner=User.objects.create())
        section_type = SectionType.objects.create(
            name="Sample name", type="Sample type", css_class="Sample class"
        )
        section_status = SectionStatus.objects.create(status="Sample status")
        file_section = FileSection.objects.create(
            section_start=0,
            section_end=10,
            section_of=file,
            section_type=section_type,
            section_status=section_status,
        )

    def test_no_args(self):
        self.assertRaises(IntegrityError, FileSection.objects.create)

    def test_no_section_type(self):
        file = File.objects.create(name="Sample name", owner=User.objects.create())
        section_status = SectionStatus.objects.create(status="Sample status")
        self.assertRaises(
            IntegrityError,
            FileSection.objects.create,
            section_start=0,
            section_end=10,
            section_of=file,
            section_status=section_status,
        )

    def test_no_file(self):
        section_type = SectionType.objects.create(
            name="Sample name", type="Sample type", css_class="Sample class"
        )
        section_status = SectionStatus.objects.create(status="Sample status")
        self.assertRaises(
            IntegrityError,
            FileSection.objects.create,
            section_start=0,
            section_end=10,
            section_type=section_type,
            section_status=section_status,
        )

    def test_no_section_status(self):
        file = File.objects.create(name="Sample name", owner=User.objects.create())
        section_type = SectionType.objects.create(
            name="Sample name", type="Sample type", css_class="Sample class"
        )
        self.assertRaises(
            IntegrityError,
            FileSection.objects.create,
            section_start=0,
            section_end=10,
            section_of=file,
            section_type=section_type,
            section_status=None,
        )
