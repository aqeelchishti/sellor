from datetime import date

import graphene
import pytest
from django_countries import countries

from sellor.discount import DiscountValueType, VoucherType
from sellor.discount.models import Sale, Voucher
from sellor.graphql.discount.enums import (
    DiscountValueTypeEnum, VoucherTypeEnum)
from tests.api.utils import get_graphql_content


@pytest.fixture
def voucher_countries(voucher):
    voucher.countries = countries
    voucher.save(update_fields=['countries'])
    return voucher


@pytest.fixture
def sale():
    return Sale.objects.create(name='Sale', value=123)


@pytest.fixture
def voucher():
    return Voucher.objects.create(name='Voucher', discount_value=123)


def test_voucher_query(
        staff_api_client, voucher_countries, permission_manage_discounts):
    query = """
    query vouchers {
        vouchers(first: 1) {
            edges {
                node {
                    type
                    name
                    code
                    usageLimit
                    used
                    startDate
                    discountValueType
                    discountValue
                    countries {
                        code
                        country
                    }
                }
            }
        }
    }
    """
    response = staff_api_client.post_graphql(
        query, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['vouchers']['edges'][0]['node']

    assert data['type'] == voucher_countries.type.upper()
    assert data['name'] == voucher_countries.name
    assert data['code'] == voucher_countries.code
    assert data['usageLimit'] == voucher_countries.usage_limit
    assert data['used'] == voucher_countries.used
    assert data['startDate'] == voucher_countries.start_date.isoformat()
    assert data[
        'discountValueType'] == voucher_countries.discount_value_type.upper()
    assert data['discountValue'] == voucher_countries.discount_value
    assert data['countries'] == [{
        'country': country.name,
        'code': country.code} for country in voucher_countries.countries]


def test_sale_query(staff_api_client, sale, permission_manage_discounts):
    query = """
        query sales {
            sales(first: 1) {
                edges {
                    node {
                        type
                        name
                        value
                        startDate
                    }
                }
            }
        }
        """
    response = staff_api_client.post_graphql(
        query, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['sales']['edges'][0]['node']
    assert data['type'] == sale.type.upper()
    assert data['name'] == sale.name
    assert data['value'] == sale.value
    assert data['startDate'] == sale.start_date.isoformat()


CREATE_VOUCHER_MUTATION = """
mutation  voucherCreate(
    $type: VoucherTypeEnum, $name: String, $code: String,
    $discountValueType: DiscountValueTypeEnum,
    $discountValue: Decimal, $minAmountSpent: Decimal,
    $startDate: Date, $endDate: Date) {
        voucherCreate(input: {
                name: $name, type: $type, code: $code,
                discountValueType: $discountValueType,
                discountValue: $discountValue,
                minAmountSpent: $minAmountSpent,
                startDate: $startDate, endDate: $endDate}) {
            errors {
                field
                message
            }
            voucher {
                type
                minAmountSpent {
                    amount
                }
                name
                code
                discountValueType
                startDate
                endDate
            }
        }
    }
"""


def test_create_voucher(staff_api_client, permission_manage_discounts):
    start_date = date(day=1, month=1, year=2018)
    end_date = date(day=1, month=1, year=2019)
    variables = {
        'name': 'test voucher',
        'type': VoucherTypeEnum.VALUE.name,
        'code': 'testcode123',
        'discountValueType': DiscountValueTypeEnum.FIXED.name,
        'discountValue': 10.12,
        'minAmountSpent': 1.12,
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat()}

    response = staff_api_client.post_graphql(
        CREATE_VOUCHER_MUTATION,
        variables,
        permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCreate']['voucher']
    assert data['type'] == VoucherType.VALUE.upper()
    assert data['minAmountSpent']['amount'] == 1.12
    assert data['name'] == 'test voucher'
    assert data['code'] == 'testcode123'
    assert data['discountValueType'] == DiscountValueType.FIXED.upper()
    assert data['startDate'] == start_date.isoformat()
    assert data['endDate'] == end_date.isoformat()


def test_create_voucher_with_empty_code(
        staff_api_client, permission_manage_discounts):
    start_date = date(day=1, month=1, year=2018)
    end_date = date(day=1, month=1, year=2019)
    variables = {
        'name': 'test voucher',
        'type': VoucherTypeEnum.VALUE.name,
        'code': '',
        'discountValueType': DiscountValueTypeEnum.FIXED.name,
        'discountValue': 10.12,
        'minAmountSpent': 1.12,
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat()}

    response = staff_api_client.post_graphql(
        CREATE_VOUCHER_MUTATION,
        variables,
        permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCreate']['voucher']
    assert data['name'] == variables['name']
    assert data['code'] != ''


def test_update_voucher(
        staff_api_client, voucher, permission_manage_discounts):
    query = """
    mutation  voucherUpdate($code: String,
        $discountValueType: DiscountValueTypeEnum, $id: ID!) {
            voucherUpdate(id: $id, input: {
                code: $code, discountValueType: $discountValueType}) {
                errors {
                    field
                    message
                }
                voucher {
                    code
                    discountValueType
                }
            }
        }
    """
    # Set discount value type to 'fixed' and change it in mutation
    voucher.discount_value_type = DiscountValueType.FIXED
    voucher.save()
    assert voucher.code != 'testcode123'
    variables = {
        'id': graphene.Node.to_global_id('Voucher', voucher.id),
        'code': 'testcode123',
        'discountValueType': DiscountValueTypeEnum.PERCENTAGE.name}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherUpdate']['voucher']
    assert data['code'] == 'testcode123'
    assert data['discountValueType'] == DiscountValueType.PERCENTAGE.upper()


def test_voucher_delete_mutation(
        staff_api_client, voucher, permission_manage_discounts):
    query = """
        mutation DeleteVoucher($id: ID!) {
            voucherDelete(id: $id) {
                voucher {
                    name
                    id
                }
                errors {
                    field
                    message
                }
              }
            }
    """
    variables = {'id': graphene.Node.to_global_id('Voucher', voucher.id)}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherDelete']
    assert data['voucher']['name'] == voucher.name
    with pytest.raises(voucher._meta.model.DoesNotExist):
        voucher.refresh_from_db()


def test_voucher_add_catalogues(
        staff_api_client, voucher, category, product, collection,
        permission_manage_discounts):
    query = """
        mutation voucherCataloguesAdd($id: ID!, $input: CatalogueInput!) {
            voucherCataloguesAdd(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    product_id = graphene.Node.to_global_id('Product', product.id)
    collection_id = graphene.Node.to_global_id('Collection', collection.id)
    category_id = graphene.Node.to_global_id('Category', category.id)
    variables = {
        'id': graphene.Node.to_global_id('Voucher', voucher.id),
        'input': {
            'products': [product_id],
            'collections': [collection_id],
            'categories': [category_id]}}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCataloguesAdd']

    assert not data['errors']
    assert product in voucher.products.all()
    assert category in voucher.categories.all()
    assert collection in voucher.collections.all()


def test_voucher_remove_catalogues(
        staff_api_client, voucher, category, product, collection,
        permission_manage_discounts):
    voucher.products.add(product)
    voucher.collections.add(collection)
    voucher.categories.add(category)

    query = """
        mutation voucherCataloguesRemove($id: ID!, $input: CatalogueInput!) {
            voucherCataloguesRemove(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    product_id = graphene.Node.to_global_id('Product', product.id)
    collection_id = graphene.Node.to_global_id('Collection', collection.id)
    category_id = graphene.Node.to_global_id('Category', category.id)
    variables = {
        'id': graphene.Node.to_global_id('Voucher', voucher.id),
        'input': {
            'products': [product_id],
            'collections': [collection_id],
            'categories': [category_id]}}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCataloguesRemove']

    assert not data['errors']
    assert product not in voucher.products.all()
    assert category not in voucher.categories.all()
    assert collection not in voucher.collections.all()


def test_voucher_add_no_catalogues(
        staff_api_client, voucher, permission_manage_discounts):
    query = """
        mutation voucherCataloguesAdd($id: ID!, $input: CatalogueInput!) {
            voucherCataloguesAdd(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    variables = {
        'id': graphene.Node.to_global_id('Voucher', voucher.id),
        'input': {
            'products': [],
            'collections': [],
            'categories': []}}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCataloguesAdd']

    assert not data['errors']
    assert not voucher.products.exists()
    assert not voucher.categories.exists()
    assert not voucher.collections.exists()


def test_voucher_remove_no_catalogues(
        staff_api_client, voucher, category, product, collection,
        permission_manage_discounts):
    voucher.products.add(product)
    voucher.collections.add(collection)
    voucher.categories.add(category)

    query = """
            mutation voucherCataloguesAdd($id: ID!, $input: CatalogueInput!) {
                voucherCataloguesAdd(id: $id, input: $input) {
                    errors {
                        field
                        message
                    }
                }
            }
        """
    variables = {
        'id': graphene.Node.to_global_id('Voucher', voucher.id),
        'input': {
            'products': [],
            'collections': [],
            'categories': []}}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCataloguesAdd']

    assert not data['errors']
    assert voucher.products.exists()
    assert voucher.categories.exists()
    assert voucher.collections.exists()


def test_create_sale(staff_api_client, permission_manage_discounts):
    query = """
    mutation  saleCreate(
            $type: DiscountValueTypeEnum, $name: String, $value: Decimal,
            $startDate: Date, $endDate: Date) {
        saleCreate(input: {
                name: $name, type: $type, value: $value,
                startDate: $startDate, endDate: $endDate}) {
            sale {
                type
                name
                value
                startDate
                endDate
            }
            errors {
                field
                message
            }
        }
    }
    """
    start_date = date(day=1, month=1, year=2018)
    end_date = date(day=1, month=1, year=2019)
    variables = {
        'name': 'test sale',
        'type': DiscountValueTypeEnum.FIXED.name,
        'value': '10.12',
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat()}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleCreate']['sale']

    assert data['type'] == DiscountValueType.FIXED.upper()
    assert data['name'] == 'test sale'
    assert data['value'] == 10.12
    assert data['startDate'] == start_date.isoformat()
    assert data['endDate'] == end_date.isoformat()


def test_update_sale(staff_api_client, sale, permission_manage_discounts):
    query = """
    mutation  saleUpdate($type: DiscountValueTypeEnum, $id: ID!) {
            saleUpdate(id: $id, input: {type: $type}) {
                errors {
                    field
                    message
                }
                sale {
                    type
                }
            }
        }
    """
    # Set discount value type to 'fixed' and change it in mutation
    sale.type = DiscountValueType.FIXED
    sale.save()
    variables = {
        'id': graphene.Node.to_global_id('Sale', sale.id),
        'type': DiscountValueTypeEnum.PERCENTAGE.name}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleUpdate']['sale']
    assert data['type'] == DiscountValueType.PERCENTAGE.upper()


def test_sale_delete_mutation(
        staff_api_client, sale, permission_manage_discounts):
    query = """
        mutation DeleteSale($id: ID!) {
            saleDelete(id: $id) {
                sale {
                    name
                    id
                }
                errors {
                    field
                    message
                }
              }
            }
    """
    variables = {'id': graphene.Node.to_global_id('Sale', sale.id)}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleDelete']
    assert data['sale']['name'] == sale.name
    with pytest.raises(sale._meta.model.DoesNotExist):
        sale.refresh_from_db()


def test_sale_add_catalogues(
        staff_api_client, sale, category, product, collection,
        permission_manage_discounts):
    query = """
        mutation saleCataloguesAdd($id: ID!, $input: CatalogueInput!) {
            saleCataloguesAdd(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    product_id = graphene.Node.to_global_id('Product', product.id)
    collection_id = graphene.Node.to_global_id('Collection', collection.id)
    category_id = graphene.Node.to_global_id('Category', category.id)
    variables = {
        'id': graphene.Node.to_global_id('Sale', sale.id),
        'input': {
            'products': [product_id],
            'collections': [collection_id],
            'categories': [category_id]}}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleCataloguesAdd']

    assert not data['errors']
    assert product in sale.products.all()
    assert category in sale.categories.all()
    assert collection in sale.collections.all()


def test_sale_remove_catalogues(
        staff_api_client, sale, category, product, collection,
        permission_manage_discounts):
    sale.products.add(product)
    sale.collections.add(collection)
    sale.categories.add(category)

    query = """
        mutation saleCataloguesRemove($id: ID!, $input: CatalogueInput!) {
            saleCataloguesRemove(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    product_id = graphene.Node.to_global_id('Product', product.id)
    collection_id = graphene.Node.to_global_id('Collection', collection.id)
    category_id = graphene.Node.to_global_id('Category', category.id)
    variables = {
        'id': graphene.Node.to_global_id('Sale', sale.id),
        'input': {
            'products': [product_id],
            'collections': [collection_id],
            'categories': [category_id]}}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleCataloguesRemove']

    assert not data['errors']
    assert product not in sale.products.all()
    assert category not in sale.categories.all()
    assert collection not in sale.collections.all()


def test_sale_add_no_catalogues(
        staff_api_client, sale, permission_manage_discounts):
    query = """
        mutation saleCataloguesAdd($id: ID!, $input: CatalogueInput!) {
            saleCataloguesAdd(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    variables = {
        'id': graphene.Node.to_global_id('Sale', sale.id),
        'input': {
            'products': [],
            'collections': [],
            'categories': []}}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleCataloguesAdd']

    assert not data['errors']
    assert not sale.products.exists()
    assert not sale.categories.exists()
    assert not sale.collections.exists()


def test_sale_remove_no_catalogues(
        staff_api_client, sale, category, product, collection,
        permission_manage_discounts):
    sale.products.add(product)
    sale.collections.add(collection)
    sale.categories.add(category)

    query = """
        mutation saleCataloguesAdd($id: ID!, $input: CatalogueInput!) {
            saleCataloguesAdd(id: $id, input: $input) {
                errors {
                    field
                    message
                }
            }
        }
    """
    variables = {
        'id': graphene.Node.to_global_id('Sale', sale.id),
        'input': {
            'products': [],
            'collections': [],
            'categories': []}}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleCataloguesAdd']

    assert not data['errors']
    assert sale.products.exists()
    assert sale.categories.exists()
    assert sale.collections.exists()
