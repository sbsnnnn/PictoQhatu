from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.main import create_app


def test_sirve_el_build_del_frontend_sin_tapar_ws_ni_pictos(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<h1>PictoQhatu</h1>", encoding="utf-8")
    (tmp_path / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    app = create_app(Settings(dist=tmp_path))

    with TestClient(app) as client:
        assert "PictoQhatu" in client.get("/").text
        assert client.get("/assets/app.js").text == "console.log(1)"
        assert client.get("/pictos/pan.png").status_code == 200
        with client.websocket_connect("/ws/sala1") as ws:
            ws.send_json({"type": "join", "avatar": "manzana"})
            assert ws.receive_json()["type"] == "joined"


def test_sin_build_el_backend_arranca_igual(tmp_path):
    app = create_app(Settings(dist=tmp_path / "no_existe"))
    with TestClient(app) as client:
        assert client.get("/").status_code == 404
