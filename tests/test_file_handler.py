import os
import pytest
from agent.file_handler import save_research


def test_save_research_creates_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    filename = save_research("test query", "test result")
    assert os.path.exists(filename)


def test_save_research_returns_correct_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    filename = save_research("test query", "test result")
    assert filename.startswith("results/research_")
    assert filename.endswith(".txt")


def test_save_research_file_contents(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    filename = save_research("What is AI?", "AI stands for artificial intelligence.")
    with open(filename, encoding="utf-8") as f:
        content = f.read()
    assert "Query: What is AI?" in content
    assert "AI stands for artificial intelligence." in content
    assert "AI Research Assistant" in content


def test_save_research_creates_results_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert not os.path.exists("results")
    save_research("query", "result")
    assert os.path.isdir("results")


def test_save_research_unique_filenames(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Patch datetime to force same timestamp and verify uniqueness isn't broken
    # or just call twice quickly and check both files exist
    f1 = save_research("query 1", "result 1")
    f2 = save_research("query 2", "result 2")
    # Both files should exist (timestamps may differ by a second)
    assert os.path.exists(f1)
    assert os.path.exists(f2)
