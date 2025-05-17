import pytest

from application.models.sql_query.select import SelectClause
from application.models.sql_query.column_item import ColumnItem


@pytest.mark.parametrize(('input_text', 'expected_objects'), (
    ('*', [ColumnItem(field='*')]),
    ('id, name, email', [ColumnItem(field='id'), ColumnItem(field='name'), ColumnItem(field='email')]),
    ('first_name, last_name, COUNT(*) AS num_orders', [ColumnItem(field='first_name'), ColumnItem(field='last_name'), ColumnItem(field='*', func='COUNT', as_name='num_orders')]),
    ('products.name, SUM(order_items.quantity) AS total_sold', [ColumnItem(field='products.name'),ColumnItem(field='order_items.quantity', func='SUM', as_name='total_sold')]),
    ('customers.name AS customer_name, COUNT(orders.id) AS num_orders, AVG(order_items.quantity) AS avg_quantity', [ColumnItem(field='customers.name', as_name='customer_name'), ColumnItem(field='orders.id', func='COUNT', as_name='num_orders'), ColumnItem(field='order_items.quantity', func='AVG', as_name='avg_quantity')]),
    ('department, AVG(salary) AS avg_salary', [ColumnItem(field='department'), ColumnItem(field='salary', func='AVG', as_name='avg_salary')]),
))
def test_select_conversions(input_text, expected_objects):
    output_select = SelectClause.process(input_text)
    assert output_select == expected_objects

# def test_agg_dict():
#     column_items = [ColumnItem(field='customers.name', as_name='customer_name'), ColumnItem(field='orders.id', func='COUNT', as_name='num_orders'), ColumnItem(field='order_items.quantity', func='AVG', as_name='avg_quantity'), ColumnItem(field='*', func='COUNT', as_name='num_orders')]
#     select_clause = select.SelectClause(column_items)

#     expected_agg_dict = {
#         'mean_order_items.quantity': ('order_items.quantity', 'mean'),
#         'count_orders.id': ('orders.id', 'count'),
#         'count_pid': ('pid', 'count'),
#     }
#     assert select_clause.convert_items_to_agg_dict() == expected_agg_dict

