import pytest

from src.pipeline.calculator import calculate, numbers_in, ungrounded_numbers


def test_calculate_ratio_with_thousands_separators():
    assert calculate("1,664 / 25,992 * 100") == pytest.approx(6.4019, rel=1e-4)


def test_calculate_growth_rate():
    assert calculate("(18280 - 18878) / 18878 * 100") == pytest.approx(-3.1677, rel=1e-4)


@pytest.mark.parametrize("expression", ["__import__('os').system('dir')", "open('x')", "2 ** 1000", "a + 1"])
def test_calculate_rejects_anything_but_arithmetic(expression):
    with pytest.raises((ValueError, SyntaxError)):
        calculate(expression)


def test_numbers_in_parses_separators_and_signs():
    assert numbers_in("Sales were €25,992 million, down -4.4% from 27,193.") == [25992.0, -4.4, 27193.0]


def test_grounded_answer_passes():
    sources = "Net income came to €1,664 million. Sales amounted to €25,992 million."
    answer = "Net income of €1,664 million on sales of €25,992 million is a 6.4% net margin."
    assert ungrounded_numbers(answer, sources, allowed_values=[6.4019]) == []


def test_invented_number_is_flagged():
    sources = "Net income came to €1,664 million."
    assert ungrounded_numbers("Net income was €1,700 million.", sources) == [1700.0]


def test_years_and_small_counts_are_ignored():
    assert ungrounded_numbers("In 2025 the two companies...", "nothing numeric") == []


def test_million_to_billion_rescaling_is_grounded():
    assert ungrounded_numbers("Sales were €19.7 billion.", "Sales 19,676 (in € millions)") == []
