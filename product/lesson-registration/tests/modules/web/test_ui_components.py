"""Unit tests verifying Web UI 5-surface component templates and index entrypoint."""
from pathlib import Path
import unittest

WEB_DIR = Path(__file__).resolve().parents[3] / "web"


class TestWebComponents(unittest.TestCase):
    def test_components_exist_and_contain_required_markup(self):
        """Verifies that all 5 surface templates exist and have key UI elements."""
        components_dir = WEB_DIR / "components"
        self.assertTrue(components_dir.exists())

        # 1. Source Surface
        source_html = (components_dir / "source.html").read_text(encoding="utf-8")
        self.assertIn("surface-source", source_html)
        self.assertIn("btn-create-source", source_html)
        self.assertIn("source-title", source_html)

        # 2. Prepare Surface
        prep_html = (components_dir / "prepare.html").read_text(encoding="utf-8")
        self.assertIn("surface-prepare", prep_html)
        self.assertIn("prepare-platform", prep_html)
        self.assertIn("badge-ready-status", prep_html)
        self.assertIn("btn-save-prepare", prep_html)

        # 3. Auth Surface
        auth_html = (components_dir / "auth.html").read_text(encoding="utf-8")
        self.assertIn("surface-auth", auth_html)
        self.assertIn("remote-viewer-frame", auth_html)
        self.assertIn("viewer-placeholder", auth_html)
        self.assertIn("btn-auth-open", auth_html)
        self.assertIn("btn-auth-finish", auth_html)

        # 4. Review Surface
        review_html = (components_dir / "review.html").read_text(encoding="utf-8")
        self.assertIn("surface-review", review_html)
        self.assertIn("btn-submit-start", review_html)
        self.assertIn("rev-digest", review_html)
        self.assertIn("승인 후에는 취소, 변경, 롤백이 불가합니다", review_html)

        # 5. Result Surface
        result_html = (components_dir / "result.html").read_text(encoding="utf-8")
        self.assertIn("surface-result", result_html)
        self.assertIn("progress-bar-fill", result_html)
        self.assertIn("result-box", result_html)
        self.assertIn("unknown-action-guide", result_html)
        self.assertIn("result-evidence-json", result_html)

    def test_index_and_app_js(self):
        """Verifies index.html entrypoint and app.js state machine rules."""
        index_html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn("nav-tabs", index_html)
        self.assertIn("surface-source", index_html)
        self.assertIn("surface-result", index_html)
        self.assertIn("app.js", index_html)

        app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
        self.assertIn("VIEWER_READY", app_js)
        self.assertIn("VIEWER_DISPOSE", app_js)
        self.assertIn("no-store", app_js)
        self.assertIn("X-Mock-Owner", app_js)
        self.assertIn("/v1/registrations/", app_js)


if __name__ == "__main__":
    unittest.main()
