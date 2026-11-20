from decimal import Decimal
import pytest
from app.errors import DataError
from app.modules.domain.rule import evaluate


def test_accessible_detour(cases):
    # TRAP-103
    actual, proof = evaluate(cases['accessible_detour'])
    assert actual == Decimal('120')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['桥头 → 学校'])) == Decimal('75')


def test_shortest_network(cases):
    actual, proof = evaluate(cases['shortest_network'])
    assert actual == Decimal('65')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['巷口 → 终点'])) == Decimal('25')


def test_closed_shortcut(cases):
    actual, proof = evaluate(cases['closed_shortcut'])
    assert actual == Decimal('110')
    assert str(dict((label, value) for label, value, _ in proof)['甲>丙']) == '封闭'


def test_exact_limits(cases):
    actual, proof = evaluate(cases['exact_limits'])
    assert actual == Decimal('15')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['甲 → 乙'])) == Decimal('15')


def test_same_point(cases):
    actual, proof = evaluate(cases['same_point'])
    assert actual == Decimal('0')
    assert str(dict((label, value) for label, value, _ in proof)['到达']) == '甲'


def test_cycle(cases):
    actual, proof = evaluate(cases['cycle'])
    assert actual == Decimal('35')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['乙 → 丙'])) == Decimal('25')


def test_no_reverse(cases):
    # TRAP-102
    with pytest.raises(DataError) as error:
        evaluate(cases['no_reverse'])
    assert error.value.code == 'ROAD_UNREACHABLE'


def test_duplicate_road(cases):
    with pytest.raises(DataError) as error:
        evaluate(cases['duplicate_road'])
    assert error.value.code == 'ROAD_CONFLICT'


def test_steep_descent(cases):
    with pytest.raises(DataError) as error:
        evaluate(cases['steep_descent'])
    assert error.value.code == 'ROAD_UNREACHABLE'
