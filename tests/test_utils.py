import pytest
import typer
from unittest.mock import MagicMock
from cortexapps_cli.utils import (
    guess_data_key,
    get_value_at_path,
    matches_filters,
    humanize_value,
    print_output,
    print_output_with_context,
)


# Task 1: guess_data_key edge cases (Lines 25, 31, 34, 38)

def test_guess_data_key_list_returns_empty_string():
    assert guess_data_key([1, 2, 3]) == ''


def test_guess_data_key_dict_no_list_raises():
    with pytest.raises(ValueError, match="does not contain a list"):
        guess_data_key({"key": "value"})


def test_guess_data_key_dict_multiple_lists_raises():
    with pytest.raises(ValueError, match="contains multiple lists"):
        guess_data_key({"a": [1], "b": [2]})


def test_guess_data_key_non_list_non_dict_raises():
    with pytest.raises(ValueError, match="is not a list or dict"):
        guess_data_key("a string")


# Task 2: get_value_at_path edge cases (Lines 58-62, 64-65)

def test_get_value_at_path_list_index():
    data = {"items": [{"name": "first"}, {"name": "second"}]}
    assert get_value_at_path(data, "items.1.name") == "second"


def test_get_value_at_path_non_dict_non_list_returns_none():
    data = {"key": 42}
    assert get_value_at_path(data, "key.nested") is None


def test_get_value_at_path_invalid_list_index_returns_none():
    data = {"items": [1, 2]}
    assert get_value_at_path(data, "items.abc") is None


def test_get_value_at_path_index_out_of_range_returns_none():
    data = {"items": [1]}
    assert get_value_at_path(data, "items.99") is None


# Task 3: matches_filters and humanize_value (Lines 80-87, 102, 104)

def test_matches_filters_matching():
    data = {"name": "foo", "status": "active"}
    assert matches_filters(data, ["name=foo"]) is True


def test_matches_filters_no_match():
    data = {"name": "foo"}
    assert matches_filters(data, ["name=bar"]) is False


def test_matches_filters_missing_key():
    data = {"name": "foo"}
    assert matches_filters(data, ["missing=.*"]) is False


def test_matches_filters_multiple_all_match():
    data = {"name": "foo", "status": "active"}
    assert matches_filters(data, ["name=foo", "status=active"]) is True


def test_matches_filters_multiple_one_fails():
    data = {"name": "foo", "status": "active"}
    assert matches_filters(data, ["name=foo", "status=inactive"]) is False


def test_humanize_value_list():
    assert humanize_value(["a", "b", "c"]) == "a, b, c"


def test_humanize_value_dict():
    result = humanize_value({"key": "val"})
    assert '"key": "val"' in result


def test_humanize_value_none():
    assert humanize_value(None) == ""


def test_humanize_value_string():
    assert humanize_value("hello") == "hello"


# Task 4: print_output table/csv/sort/filter paths

def test_print_output_none_format_defaults_to_json(capsys):
    print_output({"key": "val"}, output_format=None)
    out = capsys.readouterr().out
    assert "key" in out


def test_print_output_invalid_format_raises():
    with pytest.raises(ValueError, match="Invalid output format"):
        print_output({}, output_format="xml")


def test_print_output_json_with_columns_raises():
    with pytest.raises(typer.BadParameter, match="Columns can only be specified"):
        print_output({"items": [{"a": 1}]}, columns=["a"], output_format="json")


def test_print_output_json_with_filters_raises():
    with pytest.raises(typer.BadParameter, match="Filters can only be specified"):
        print_output({"items": [{"a": 1}]}, filters=["a=1"], output_format="json")


def test_print_output_table_no_columns_raises():
    with pytest.raises(typer.BadParameter, match="Columns must be specified"):
        print_output({"items": [{"a": 1}]}, output_format="table")


def test_print_output_table_shorthand_column(capsys):
    data = {"items": [{"name": "foo"}, {"name": "bar"}]}
    print_output(data, columns=["name"], output_format="table")
    out = capsys.readouterr().out
    assert "foo" in out
    assert "bar" in out


def test_print_output_table_invalid_column_format_raises():
    data = {"items": [{"a": 1}]}
    with pytest.raises(typer.BadParameter, match="Columns must be in the format"):
        print_output(data, columns=["!!!invalid"], output_format="table")


def test_print_output_table_with_filters(capsys):
    data = {"items": [{"name": "foo", "status": "active"}, {"name": "bar", "status": "inactive"}]}
    print_output(data, columns=["Name=name"], filters=["status=active"], output_format="table")
    out = capsys.readouterr().out
    assert "foo" in out
    assert "bar" not in out


def test_print_output_table_invalid_filter_raises():
    data = {"items": [{"a": 1}]}
    with pytest.raises(typer.BadParameter, match="Filters must be in the format"):
        print_output(data, columns=["a"], filters=["!!!"], output_format="table")


def test_print_output_table_sort_asc(capsys):
    data = {"items": [{"name": "b"}, {"name": "a"}]}
    print_output(data, columns=["name"], sort=["name:asc"], output_format="table")
    out = capsys.readouterr().out
    assert out.index("a") < out.index("b")


def test_print_output_table_sort_desc(capsys):
    data = {"items": [{"name": "zebra"}, {"name": "apple"}]}
    print_output(data, columns=["name"], sort=["name:desc"], output_format="table")
    out = capsys.readouterr().out
    assert out.index("zebra") < out.index("apple")


def test_print_output_table_invalid_sort_raises():
    data = {"items": [{"a": 1}]}
    with pytest.raises(typer.BadParameter, match="Sort must be in the format"):
        print_output(data, columns=["a"], sort=["bad_sort"], output_format="table")


def test_print_output_csv(capsys):
    data = {"items": [{"name": "foo"}, {"name": "bar"}]}
    print_output(data, columns=["Name=name"], output_format="csv")
    out = capsys.readouterr().out
    lines = out.strip().split("\n")
    assert lines[0] == "Name"
    assert lines[1] == "foo"
    assert lines[2] == "bar"


def test_print_output_csv_no_headers(capsys):
    data = {"items": [{"name": "foo"}]}
    print_output(data, columns=["Name=name"], output_format="csv", no_headers=True)
    out = capsys.readouterr().out
    lines = out.strip().split("\n")
    assert lines[0] == "foo"
    assert "Name" not in out


# Task 5: print_output_with_context (Lines 195, 199)

def test_print_output_with_context_table_and_csv_raises():
    ctx = MagicMock()
    ctx.params = {
        "columns": ["name"],
        "filters": None,
        "sort": None,
        "table_output": True,
        "csv_output": True,
        "no_headers": False,
    }
    with pytest.raises(typer.BadParameter, match="Only one of --table and --csv"):
        print_output_with_context(ctx, {"items": [{"name": "foo"}]})


def test_print_output_with_context_csv(capsys):
    ctx = MagicMock()
    ctx.params = {
        "columns": ["Name=name"],
        "filters": None,
        "sort": None,
        "table_output": False,
        "csv_output": True,
        "no_headers": False,
    }
    print_output_with_context(ctx, {"items": [{"name": "foo"}]})
    out = capsys.readouterr().out
    assert "foo" in out
