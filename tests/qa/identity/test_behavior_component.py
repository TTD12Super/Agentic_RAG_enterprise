import unittest

from _baseline import API, IDENTITY, MAIN, read


class IdentityBehaviorTests(unittest.TestCase):
    def test_identity_package_exists(self):
        self.assertTrue((IDENTITY / "__init__.py").is_file())

    def test_identity_models_exist(self):
        self.assertTrue((IDENTITY / "models.py").is_file())

    def test_identity_store_exists(self):
        self.assertTrue((IDENTITY / "store.py").is_file())

    def test_identity_service_exists(self):
        self.assertTrue((IDENTITY / "service.py").is_file())

    def test_structured_errors_exist(self):
        self.assertTrue((IDENTITY / "errors.py").is_file())

    def test_identity_router_exists(self):
        self.assertTrue((API / "identity.py").is_file())

    def test_sign_in_route_exists(self):
        self.assertIn('@router.post("/sign-in"', read(API / "identity.py"))

    def test_current_identity_route_exists(self):
        self.assertIn('@router.get("/me"', read(API / "identity.py"))

    def test_sign_out_route_exists(self):
        self.assertIn('@router.post("/sign-out"', read(API / "identity.py"))

    def test_router_uses_versioned_api_prefix(self):
        self.assertIn('prefix=settings.api_prefix', read(MAIN))


if __name__ == "__main__":
    unittest.main()
