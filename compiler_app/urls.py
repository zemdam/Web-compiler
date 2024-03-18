from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = "web_compiler"
urlpatterns = [
    path("", views.index, name="index"),
    path("file/<int:file_id>/", views.open_file, name="open_file"),
    path("catalog/<int:catalog_id>/", views.open_catalog, name="open_catalog"),
    path("add_catalog/<int:catalog_id>/", views.add_catalog, name="add_catalog"),
    path("add_file/<int:catalog_id>/", views.add_file, name="add_file"),
    path(
        "delete_catalog/<int:catalog_id>/", views.delete_catalog, name="delete_catalog"
    ),
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
    path("compiled_file/<int:file_id>/", views.compiled_file, name="compiled_file"),
    path(
        "download_compiled_file/<int:file_id>/",
        views.download_compiled_file,
        name="download_compiled_file",
    ),
    path("set_compile_options/", views.set_compile_options, name="set_compile_options"),
    path("login/", LoginView.as_view(next_page="/compiler/"), name="login"),
    path("logout/", LogoutView.as_view(next_page="/compiler/login/"), name="logout"),
    path("add_section/<int:file_id>/", views.add_section, name="add_section"),
]
