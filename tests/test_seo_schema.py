import json

import pytest

from sellor.seo.schema.email import (
    get_order_confirmation_markup, get_organization, get_product_data)


def test_get_organization(site_settings):
    example_name = 'sellor Brand Name'
    site = site_settings.site
    site.name = example_name
    site.save()

    result = get_organization()
    assert result['name'] == example_name


def test_get_product_data_without_image(order_with_lines):
    """Tested OrderLine Product has no image assigned."""
    line = order_with_lines.lines.first()
    organization = get_organization()
    result = get_product_data(line, organization)
    assert 'image' not in result['itemOffered']


def test_get_product_data_with_image(order_with_lines, product_with_image):
    line = order_with_lines.lines.first()
    variant = product_with_image.variants.first()
    line.variant = variant
    line.product_name = variant.display_product()
    line.save()
    organization = get_organization()
    result = get_product_data(line, organization)
    assert 'image' in result['itemOffered']
    assert result['itemOffered']['name'] == variant.display_product()


def test_get_order_confirmation_markup(order_with_lines):
    try:
        result = get_order_confirmation_markup(order_with_lines)
    except TypeError:
        pytest.fail('Function output is not JSON serializable')

    try:
        # Response should be returned as a valid json
        json.loads(result)
    except ValueError:
        pytest.fail('Response is not a valid json')
