from typing import Any, Dict
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils.timezone import now
from django.urls import reverse
from django.http import HttpResponseRedirect, FileResponse
from django.contrib.auth.decorators import login_required
from os.path import splitext, split
import subprocess
import re

from .models import Catalog, File, FileSection, SectionType, SectionStatus
from .forms import (
    NewCatalogForm,
    AddSectionForm,
    StandardForm,
    OptimizationsForm,
    ProcessorForm,
    OptionsMCS51Form,
    OptionsZ80Form,
    OptionsSTM8Form,
    Options,
    UploadFileForm,
)


def get_basic_context(user, session):
    basic_context = {
        "catalogs": Catalog.objects.all().filter(owner=user, holder=None),
        "files": File.objects.all().filter(owner=user, holder=None),
        "newCatalogForm": NewCatalogForm(),
        "standardForm": StandardForm(initial=session.get("standard", None)),
        "optimizationsForm": OptimizationsForm(
            initial=session.get("optimizations", None)
        ),
        "processorForm": ProcessorForm(initial=session.get("processor", None)),
        "optionsMCS51Form": OptionsMCS51Form(initial=session.get("proc_option1", None)),
        "optionsZ80Form": OptionsZ80Form(initial=session.get("proc_option1", None)),
        "optionsSTM8Form": OptionsSTM8Form(initial=session.get("proc_option1", None)),
        "uploadFileForm": UploadFileForm(),
    }
    return basic_context


@login_required(login_url="/compiler/login")
def index(request):
    return render(
        request, "index.html", get_basic_context(request.user, request.session)
    )


class LinedFileSection:
    pass


class NumedLine:
    pass


def get_lined_sections(file_sections):
    result = list()
    line_num = 1

    for section in file_sections:
        result.append(LinedFileSection())
        result[-1].lines = list()
        result[-1].css_class = section.section_type.css_class
        result[-1].title = section.section_type.name
        for line in section.section_data.splitlines():
            result[-1].lines.append(NumedLine())
            result[-1].lines[-1].data = line + "\n"
            result[-1].lines[-1].num = line_num
            line_num += 1

    return result


def open_file_context(file, request):
    context = get_basic_context(request.user, request.session)
    context["file_content"] = get_lined_sections(
        file.filesection_set.all().order_by("section_start")
    )
    context["current_file"] = file
    context["current_catalog"] = file.holder
    context["addSectionForm"] = AddSectionForm(initial={"section_of": file})

    return context


@login_required(login_url="/compiler/login")
def open_file(request, file_id):
    current_file = get_object_or_404(File, pk=file_id, owner=request.user)
    context = open_file_context(current_file, request)

    return render(request, "index.html", context)


@login_required(login_url="/compiler/login")
def open_catalog(request, catalog_id):
    current_catalog = get_object_or_404(Catalog, pk=catalog_id, owner=request.user)
    context = get_basic_context(request.user, request.session)
    context["current_catalog"] = current_catalog
    return render(request, "index.html", context)


def update_content_change_date(catalog):
    catalog.content_change_date = now()
    catalog.save()
    if catalog.holder:
        update_content_change_date(catalog.holder)


@login_required(login_url="/compiler/login")
def add_catalog(request, catalog_id):
    if request.method == "POST":
        form = NewCatalogForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            holder = Catalog.objects.filter(pk=catalog_id, owner=request.user).first()
            catalog = Catalog(name=name, holder=holder, owner=request.user)
            if holder:
                update_content_change_date(holder)
            catalog.save()
            return HttpResponseRedirect(
                reverse("web_compiler:open_catalog", args=(catalog.id,))
            )

    context = get_basic_context(request.user, request.session)
    context["add_to_catalog_id"] = catalog_id
    context["current_catalog"] = Catalog.objects.filter(
        pk=catalog_id, owner=request.user
    ).first()
    return render(request, "index.html", context)


def find_section_type(line):
    if re.match("^[ \t]*#", line):
        return SectionType.objects.get(type="Compiler directive")

    if re.match("^[ \t]*//", line):
        return SectionType.objects.get(type="Comment")

    return SectionType.objects.get(type="Other")


def parse_file(file):
    with file.actual_file.open("r") as f:
        currentSection = None
        currentLine = 0
        for line in f:
            type = find_section_type(line)
            if currentSection and currentSection.section_type == type:
                currentSection.section_data += line
                currentSection.section_end = currentLine
            else:
                if currentSection:
                    currentSection.save()
                currentSection = FileSection(
                    section_start=currentLine,
                    section_end=currentLine,
                    section_type=type,
                    section_data=line,
                    section_of=file,
                )
            currentLine += 1
        if currentSection:
            currentSection.save()


@login_required(login_url="/compiler/login")
def add_file(request, catalog_id):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        name = request.FILES["actual_file"].name
        holder = Catalog.objects.filter(pk=catalog_id, owner=request.user).first()
        if holder:
            update_content_change_date(holder)
        file = File(
            name=name,
            holder=holder,
            owner=request.user,
            actual_file=request.FILES["actual_file"],
        )
        file.save()
        parse_file(file)
        return HttpResponseRedirect(reverse("web_compiler:open_file", args=(file.id,)))

    next = request.POST.get("next", "/compiler")

    return HttpResponseRedirect(next)


@login_required(login_url="/compiler/login")
def delete_file(request, file_id):
    file = get_object_or_404(File, pk=file_id, owner=request.user)
    file.available = False
    file.availability_change_date = now()
    file.save()
    if file.holder:
        update_content_change_date(file.holder)
        return HttpResponseRedirect(
            reverse("web_compiler:open_catalog", args=(file.holder.id,))
        )
    return HttpResponseRedirect(reverse("web_compiler:index"))


def change_availability(catalog):
    catalog.available = False
    catalog.availability_change_date = now()

    for file in catalog.file_set.all():
        file.available = False
        file.availability_change_date = now()
        file.save()

    for next_catalog in catalog.catalog_set.all():
        change_availability(next_catalog)

    catalog.save()


@login_required(login_url="/compiler/login")
def delete_catalog(request, catalog_id):
    catalog = get_object_or_404(Catalog, pk=catalog_id, owner=request.user)
    change_availability(catalog)
    if catalog.holder:
        update_content_change_date(catalog.holder)
        return HttpResponseRedirect(
            reverse("web_compiler:open_catalog", args=(catalog.holder.id,))
        )
    return HttpResponseRedirect(reverse("web_compiler:index"))


def add_to_list(my_list, val):
    if val:
        to_add = list(val.values())
        for el in to_add:
            if type(el) is list:
                my_list.extend(el)
            else:
                my_list.append(el)


class CompiledFileSection:
    pass


class ContentPart:
    pass


@login_required(login_url="/compiler/login")
def compiled_file(request, file_id):
    file = get_object_or_404(File, pk=file_id, owner=request.user)
    open("compiled.asm", "w+").close()
    run_list = ["sdcc", "-S", "-o", "compiled.asm"]

    add_to_list(run_list, request.session.get("standard", None))
    add_to_list(run_list, request.session.get("optimizations", None))
    add_to_list(run_list, request.session.get("processor", None))
    add_to_list(run_list, request.session.get("proc_option1", None))

    run_list.append(file.actual_file.path)
    run_out = subprocess.run(run_list, capture_output=True, text=True)
    context = open_file_context(file, request)

    result = list()
    if run_out.returncode != 0:
        result.append(CompiledFileSection())
        result[-1].content = run_out.stderr
        f = open("compiled.asm", "w+")
        f.write(run_out.stderr)
        f.close()
        result[-1].css_class = "section__error"
        result[-1].rest = ""
    else:
        f = open("compiled.asm", "r")
        compiled_file_content = f.readlines()
        f.close()

        is_header = False
        id = 0
        for line in compiled_file_content:
            if re.match("^;-", line):
                if is_header:
                    result[-1].content += line
                    is_header = False
                    result.append(CompiledFileSection())
                    result[-1].content = ""
                    result[-1].css_class = "section__content"
                    result[-1].rest = f"id=header-{id}"
                    id += 1
                else:
                    result.append(CompiledFileSection())
                    result[-1].content = line
                    result[-1].css_class = "section__header"
                    result[-1].rest = f"onclick=hideHeader('#header-{id}')"
                    is_header = True
            else:
                result[-1].content += line

    for res in result:
        res.content = re.sub(
            r"\.c:\s*(\d+)(.*)",
            r".c:<div class='help' id='help\1' onclick='highlightLine(\1)'>\1\2</div>",
            res.content,
        )

    context["compiled_file_content"] = result

    return render(request, "index.html", context)


@login_required(login_url="/compiler/login")
def download_compiled_file(request, file_id):
    file = get_object_or_404(File, pk=file_id, owner=request.user)
    name = splitext(file.name)[0]
    return FileResponse(open("compiled.asm", "rb"), filename=name + ".asm")


@login_required(login_url="/compiler/login")
def set_compile_options(request):
    tab_id = request.POST.get("tab_id")
    next = request.POST.get("next", "/compiler")

    form = StandardForm(request.POST)
    if form.is_valid():
        request.session["standard"] = form.cleaned_data

    form = OptimizationsForm(request.POST)
    if form.is_valid():
        request.session["optimizations"] = form.cleaned_data

    form = ProcessorForm(request.POST)
    if form.is_valid():
        prev_proc = request.session["processor"]
        request.session["processor"] = form.cleaned_data
        if prev_proc == form.cleaned_data:
            if form.cleaned_data["processor"] == "-mmcs51":
                form = OptionsMCS51Form(request.POST)
            elif form.cleaned_data["processor"] == "-mz80":
                form = OptionsZ80Form(request.POST)
            elif form.cleaned_data["processor"] == "-mstm8":
                form = OptionsSTM8Form(request.POST)

            if form.is_valid() and isinstance(form, Options):
                request.session["proc_option1"] = form.cleaned_data
        else:
            request.session["proc_option1"] = None

    if "compiled_file" in next:
        return HttpResponseRedirect(
            reverse("web_compiler:open_file", args=(split(split(next)[0])[1],))
        )

    return HttpResponseRedirect(next)


def get_lines_from_file(section, file):
    with file.actual_file.open("r") as f:
        result = f.readlines()[section.section_start : section.section_end + 1]
        return "".join(result)


def handle_changed_section(section, file):
    if section.section_end < section.section_start:
        if section.id:
            section.delete()
    else:
        section.section_data = get_lines_from_file(section, file)
        section.save()


def fix_sections(start, end, file):
    file.filesection_set.all().filter(
        section_start__gt=start, section_end__lt=end
    ).delete()
    section_above = (
        file.filesection_set.all()
        .filter(section_start__lte=start, section_end__gte=start)
        .first()
    )
    section_below = (
        file.filesection_set.all()
        .filter(section_start__lte=end, section_end__gte=end)
        .first()
    )
    if section_above == section_below:
        section_below.pk = None
    section_above.section_end = start - 1
    section_below.section_start = end + 1
    handle_changed_section(section_above, file)
    handle_changed_section(section_below, file)


@login_required(login_url="/compiler/login")
def add_section(request, file_id):
    file = get_object_or_404(File, pk=file_id, owner=request.user)
    form = AddSectionForm(request.POST)

    if form.is_valid() and form.cleaned_data["section_of"] == file:
        section_start = form.cleaned_data["section_start"]
        section_end = form.cleaned_data["section_end"]
        section_type = form.cleaned_data["section_type"]
        section = FileSection(
            section_start=section_start,
            section_end=section_end,
            section_type=section_type,
            section_of=file,
        )
        section.section_data = get_lines_from_file(section, file)
        fix_sections(section_start, section_end, file)
        section.save()

    return HttpResponseRedirect(reverse("web_compiler:open_file", args=(file_id,)))


# Create your views here.
