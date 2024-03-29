# Generated by Django 2.0.2 on 2018-03-11 18:54
import html

from django.core.validators import MaxLengthValidator
from django.db import migrations, models
from sellor.core.utils.text import strip_html_and_truncate


def to_seo_friendly(text):
    # sellor descriptions are stored as escaped HTML,
    # we need to decode them before processing them
    text = html.unescape(text)

    # cleanup the description and make it seo friendly
    return strip_html_and_truncate(text, 300)


def assign_seo_descriptions(apps, schema_editor):
    Product = apps.get_model('product', 'Product')
    for product in Product.objects.all():
        if product.seo_description is None:
            product.seo_description = to_seo_friendly(product.description)
            product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0052_slug_field_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='seo_description',
            field=models.CharField(
                blank=True, null=True, max_length=300,
                validators=[MaxLengthValidator(300)]),
            preserve_default=False,
        ),
        migrations.RunPython(assign_seo_descriptions)
    ]
