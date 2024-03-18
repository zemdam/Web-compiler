from django.test import TestCase
from django.urls import reverse
from ..models import User, File, Catalog, SectionType
from django.core.files.uploadedfile import SimpleUploadedFile


def redirect_compare_login(url, self):
    response = self.client.get(url, follow=True)
    self.assertRedirects(response, reverse("web_compiler:login") + f"?next={url}")


def no_redirect(url, self):
    response = self.client.get(url, follow=True)
    self.assertEqual(response.status_code, 200)


def log_in(self):
    self.user = User.objects.create_user(username="testuser", password="12345")
    self.client.login(username="testuser", password="12345")


class TestIndexView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:index"), self)

    def test_logged(self):
        log_in(self)
        no_redirect(reverse("web_compiler:index"), self)


class TestOpenFileView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:open_file", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        file = File.objects.create(
            name="Sample file name", owner=self.user, actual_file=uploaded_file
        )
        no_redirect(reverse("web_compiler:open_file", args=(file.id,)), self)


class TestOpenCatalogView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:open_catalog", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        catalog = Catalog.objects.create(name="Sample catalog name", owner=self.user)
        no_redirect(reverse("web_compiler:open_catalog", args=(catalog.id,)), self)


class TestAddCatalogView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:add_catalog", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        response = self.client.post(
            reverse("web_compiler:add_catalog", args=(0,)),
            {"name": "sample"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        catalog = Catalog.objects.filter(name="sample", owner=self.user).first()
        self.assertRedirects(
            response, reverse("web_compiler:open_catalog", args=(catalog.id,))
        )


class TestAddFileView(TestCase):
    fixtures = ["init_data"]

    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:add_file", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        response = self.client.post(
            reverse("web_compiler:add_file", args=(0,)),
            {"actual_file": uploaded_file},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        file = File.objects.filter(name="name.c", owner=self.user).first()
        self.assertRedirects(
            response, reverse("web_compiler:open_file", args=(file.id,))
        )


class TestDeleteCatalogView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:delete_catalog", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        catalog = Catalog.objects.create(name="Sample catalog name", owner=self.user)
        self.assertEqual(True, catalog.available)
        response = self.client.post(
            reverse("web_compiler:delete_catalog", args=(catalog.id,)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        catalog.refresh_from_db()
        self.assertEqual(False, catalog.available)
        self.assertRedirects(response, reverse("web_compiler:index"))


class TestDeleteFileView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:delete_file", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        file = File.objects.create(
            name="Sample file name", owner=self.user, actual_file=uploaded_file
        )
        self.assertEqual(True, file.available)
        response = self.client.post(
            reverse("web_compiler:delete_file", args=(file.id,)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        file.refresh_from_db()
        self.assertEqual(False, file.available)
        self.assertRedirects(response, reverse("web_compiler:index"))


class TestCompiledFileView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:compiled_file", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        file = File.objects.create(
            name="Sample file name", owner=self.user, actual_file=uploaded_file
        )
        response = self.client.get(
            reverse("web_compiler:compiled_file", args=(file.id,))
        )
        self.assertEqual(response.status_code, 200)


class TestDownloadCompiledFileView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(
            reverse("web_compiler:download_compiled_file", args=(0,)), self
        )

    def test_logged(self):
        log_in(self)
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        file = File.objects.create(
            name="sample", owner=self.user, actual_file=uploaded_file
        )
        response = self.client.get(
            reverse("web_compiler:compiled_file", args=(file.id,))
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse("web_compiler:download_compiled_file", args=(file.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get("Content-Disposition"), 'inline; filename="sample.asm"'
        )


class TestSetCompileOptionsView(TestCase):
    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:set_compile_options"), self)

    def test_logged(self):
        log_in(self)
        response = self.client.post(
            reverse("web_compiler:set_compile_options"),
            {"standard": "--std-c89"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("web_compiler:index"))
        self.assertEqual(self.client.session["standard"]["standard"], "--std-c89")


class TestAddSectionView(TestCase):
    fixtures = ["init_data"]

    def test_not_logged(self):
        redirect_compare_login(reverse("web_compiler:add_section", args=(0,)), self)

    def test_logged(self):
        log_in(self)
        uploaded_file = SimpleUploadedFile("name.c", b"data")
        response = self.client.post(
            reverse("web_compiler:add_file", args=(0,)),
            {"actual_file": uploaded_file},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        file = File.objects.filter(name="name.c", owner=self.user).first()
        self.assertRedirects(
            response, reverse("web_compiler:open_file", args=(file.id,))
        )
        for section in file.filesection_set.all():
            self.assertEqual(section.section_type.type, "Other")
        response = self.client.post(
            reverse("web_compiler:add_section", args=(file.id,)),
            {
                "section_start": 0,
                "section_end": 0,
                "section_type": 5,
                "section_of": file.id,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("web_compiler:open_file", args=(file.id,))
        )
        file.refresh_from_db()
        for section in file.filesection_set.all():
            self.assertEqual(section.section_type.type, "Comment")
