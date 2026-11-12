def test_health_reports_build_and_effective_model(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test-model")

    import server

    response = server.app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "build": "model-delete-v3",
        "anthropic_model": "claude-test-model",
    }
