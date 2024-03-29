from django import forms

from sellor.dashboard.product.forms import ModelChoiceOrCreationField
from sellor.product.models import Category


def test_model_choice_or_creation_field(category):
    class Form(forms.Form):
        field = ModelChoiceOrCreationField(queryset=Category.objects.all())

    form = Form({'field': category})
    assert form.is_valid()
    assert form.cleaned_data['field'] == category

    choice = 'new-value'
    form = Form({'field': choice})
    assert form.is_valid()
    assert form.cleaned_data['field'] == choice
