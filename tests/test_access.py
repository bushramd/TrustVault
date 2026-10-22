import io
import sqlite3

import pytest

from conftest import query, upload_text, user_id


def test_other_owner_cannot_download(make_client):
    doc_id = upload_text(make_client("owner1"))
    assert make_client("owner2").get(f"/documents/{doc_id}/download").status_code == 404


def test_viewer_without_grant_cannot_download(make_client):
    doc_id = upload_text(make_client("owner1"))
    assert make_client("viewer1").get(f"/documents/{doc_id}/download").status_code == 404


def test_logged_out_user_cannot_download(make_client):
    doc_id = upload_text(make_client("owner1"))
    assert make_client().get(f"/documents/{doc_id}/download").status_code == 302


def test_owner_can_download_own_file(make_client):
    doc_id = upload_text(make_client("owner1"))
    assert make_client("owner1").get(f"/documents/{doc_id}/download").status_code == 200


def test_grant_gives_access_and_revoke_removes_it(make_client):
    owner = make_client("owner1")
    viewer = make_client("viewer1")
    doc_id = upload_text(owner)
    owner.post(f"/documents/{doc_id}/share", data={"username": "viewer1", "permission": "read"})
    assert viewer.get(f"/documents/{doc_id}/download").status_code == 200
    grant_id = query("SELECT id FROM grants WHERE document_id = ?", (doc_id,))[0][0]
    owner.post(f"/documents/{doc_id}/revoke/{grant_id}")
    assert viewer.get(f"/documents/{doc_id}/download").status_code == 404


def test_reader_cannot_delete_document(make_client):
    owner = make_client("owner1")
    viewer = make_client("viewer1")
    doc_id = upload_text(owner)
    owner.post(f"/documents/{doc_id}/share", data={"username": "viewer1", "permission": "read"})
    assert viewer.post(f"/documents/{doc_id}/delete").status_code == 404
    assert query("SELECT is_deleted FROM documents WHERE id = ?", (doc_id,))[0][0] == 0


def test_non_owner_cannot_share_document(make_client):
    doc_id = upload_text(make_client("owner1"))
    resp = make_client("owner2").post(
        f"/documents/{doc_id}/share", data={"username": "viewer1", "permission": "read"}
    )
    assert resp.status_code == 404
    assert query("SELECT COUNT(*) FROM grants")[0][0] == 0


def test_deactivated_user_loses_access_immediately(make_client):
    owner = make_client("owner1")
    viewer = make_client("viewer1")
    doc_id = upload_text(owner)
    owner.post(f"/documents/{doc_id}/share", data={"username": "viewer1", "permission": "read"})
    assert viewer.get(f"/documents/{doc_id}/download").status_code == 200
    conn = sqlite3.connect(__import__("os").environ["TRUSTVAULT_DB"])
    conn.execute("UPDATE users SET is_active = 0 WHERE username = 'viewer1'")
    conn.commit()
    conn.close()
    assert viewer.get(f"/documents/{doc_id}/download").status_code == 302


def test_denied_download_is_in_audit_log(make_client):
    doc_id = upload_text(make_client("owner1"))
    make_client("viewer1").get(f"/documents/{doc_id}/download")
    rows = query(
        "SELECT outcome FROM audit_log WHERE action = 'download' AND document_id = ? AND user_id = ?",
        (doc_id, user_id("viewer1")),
    )
    assert ("denied",) in rows


def test_viewer_cannot_open_admin_page(make_client):
    assert make_client("viewer1").get("/admin").status_code == 403


def test_viewer_cannot_upload(make_client):
    assert make_client("viewer1").get("/documents/upload").status_code == 403


def test_disguised_file_is_rejected(make_client):
    owner = make_client("owner1")
    resp = owner.post(
        "/documents/upload",
        data={"file": (io.BytesIO(b"MZ not really a pdf"), "evil.pdf")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert query("SELECT COUNT(*) FROM documents")[0][0] == 0


def test_audit_log_cannot_be_changed(make_client):
    make_client("viewer1").get("/admin")
    conn = sqlite3.connect(__import__("os").environ["TRUSTVAULT_DB"])
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("UPDATE audit_log SET outcome = 'allowed'")
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM audit_log")
    conn.close()