from django import forms
from .models import FileSection, Catalog, File


class NewCatalogForm(forms.ModelForm):
    class Meta:
        model = Catalog
        fields = ["name"]
        labels = {"name": ""}


class AddSectionForm(forms.ModelForm):
    class Meta:
        model = FileSection
        fields = ["section_start", "section_end", "section_type", "section_of"]
        widgets = {
            "section_start": forms.HiddenInput(),
            "section_end": forms.HiddenInput(),
            "section_type": forms.HiddenInput(),
            "section_of": forms.HiddenInput(),
        }


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ["actual_file"]
        widgets = {
            "actual_file": forms.FileInput(
                attrs={"class": "hidden", "onChange": "sendForm(form);"}
            ),
        }
        labels = {"actual_file": ""}


class StandardForm(forms.Form):
    STANDARDS = [("--std-c89", "C89"), ("--std-c99", "C99"), ("--std-c11", "C11")]
    standard = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"onChange": "sendForm(form);"}),
        choices=STANDARDS,
        label=False,
    )


class OptimizationsForm(forms.Form):
    OPTIMIZATIONS = [
        ("--nogcse", "No gcse"),
        ("--noinvariant", "No invariant"),
        ("--noinduction", "No induction"),
    ]
    optimizations = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"onChange": "sendForm(form);"}),
        choices=OPTIMIZATIONS,
        label=False,
        required=False,
    )


class ProcessorForm(forms.Form):
    PROCESSORS = [("-mmcs51", "MCS51"), ("-mz80", "Z80"), ("-mstm8", "STM8")]
    processor = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"onChange": "sendForm(form);"}),
        choices=PROCESSORS,
        label=False,
    )


class Options(forms.Form):
    pass


class OptionsMCS51Form(Options):
    OPTIONS = [
        ("--model-large", "Model large"),
        ("--model-medium", "Model medium"),
        ("--model-small", "Model small"),
    ]
    proc_option1 = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"onChange": "sendForm(form);"}),
        choices=OPTIONS,
        label=False,
    )


class OptionsZ80Form(Options):
    OPTIONS = [
        ("--callee-saves-bc", "Callee saves bc"),
        ("--oldralloc", "Oldralloc"),
        ("--emit-externs", "Emit externs"),
    ]
    proc_option1 = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"onChange": "sendForm(form);"}),
        choices=OPTIONS,
        label=False,
        required=False,
    )


class OptionsSTM8Form(Options):
    OPTIONS1 = [("--model-large", "Model large"), ("--model-medium", "Model medium")]
    OPTIONS2 = [("--out-fmt-elf", "Out fmt elf")]
    proc_option1 = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"onChange": "sendForm(form);"}),
        choices=OPTIONS1,
        label=False,
    )
    proc_option2 = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"onChange": "sendForm(form);"}),
        choices=OPTIONS2,
        label=False,
        required=False,
    )
