import os
import random
import time
from threading import Lock
from locust import HttpUser, task, between

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://dynaman-alb-959073504.us-east-1.elb.amazonaws.com",
)

ENGINE_SERVICE_URL = os.getenv(
    "ENGINE_SERVICE_URL",
    "http://dynaman-alb-959073504.us-east-1.elb.amazonaws.com",
)

SCHEMA_ID = "People"

# -------------------------------------------------------------------
# Shared test data (read-only after setup)
# -------------------------------------------------------------------

TEST_USER_IDS = []
TEST_GROUP_IDS = []
TEST_LAYOUT_IDS = []

setup_lock = Lock()

# -------------------------------------------------------------------
# Base authenticated user
# -------------------------------------------------------------------

class AuthenticatedUser(HttpUser):
    abstract = True

    access_token: str | None = None
    token_expires_at: float = 0.0

    # -----------------------------
    # Authentication
    # -----------------------------

    def admin_login(self):
        """Login and store token + expiry (per user)."""
        res = self.client.post(
            "/api/v1/auth/token",
            data={"username": "admin@dynaman.com", "password": "admin"},
            name="auth/login/admin",
        )
        res.raise_for_status()

        data = res.json()
        self.access_token = data["access_token"]

        expires_in = data.get("expires_in", 1800)
        self.token_expires_at = time.time() + expires_in - 30  # refresh early

        self.client.headers.update(
            {"Authorization": f"Bearer {self.access_token}"}
        )

        print(f"[{self.__class__.__name__}] admin token refreshed")

    def ensure_token(self):
        """Refresh token if expired or missing."""
        if not self.access_token or time.time() >= self.token_expires_at:
            self.admin_login()

    # -----------------------------
    # Locust lifecycle
    # -----------------------------

    def on_start(self):
        # Each user authenticates itself
        self.admin_login()

        # Global one-time setup (fetch IDs)
        with setup_lock:
            if not hasattr(self.environment, "setup_done"):
                self._global_setup()
                self.environment.setup_done = True

    # -----------------------------
    # One-time setup
    # -----------------------------

    def _global_setup(self):
        print("Running one-time setup")

        # Users
        res = self.client.get("/api/v1/auth/users", name="setup/users")
        res.raise_for_status()
        for user in res.json():
            if user["email"] != "admin@dynaman.com":
                TEST_USER_IDS.append(str(user["_id"]))

        # Groups
        res = self.client.get("/api/v1/groups", name="setup/groups")
        res.raise_for_status()
        for group in res.json():
            TEST_GROUP_IDS.append(str(group["_id"]))

        # Layouts
        res = self.client.get(
            f"/api/v1/layouts/by-schema/{SCHEMA_ID}",
            name="setup/layouts",
        )
        res.raise_for_status()
        for layout in res.json():
            TEST_LAYOUT_IDS.append(str(layout["_id"]))

        print(
            f"Setup complete: "
            f"{len(TEST_USER_IDS)} users, "
            f"{len(TEST_GROUP_IDS)} groups, "
            f"{len(TEST_LAYOUT_IDS)} layouts"
        )

# -------------------------------------------------------------------
# Auth Service Users
# -------------------------------------------------------------------

class AuthServiceUser(AuthenticatedUser):
    host = AUTH_SERVICE_URL
    wait_time = between(1, 2)

    @task(3)
    def list_users_and_groups(self):
        self.ensure_token()
        self.client.get("/api/v1/auth/users", name="users/list")
        self.client.get("/api/v1/groups", name="groups/list")

    @task(2)
    def update_existing_user(self):
        if not TEST_USER_IDS:
            return
        self.ensure_token()

        user_id = random.choice(TEST_USER_IDS)
        self.client.put(
            f"/api/v1/auth/users/{user_id}",
            json={"is_active": random.choice([True, False])},
            name="users/update",
        )

    @task(1)
    def update_existing_group(self):
        if not TEST_GROUP_IDS:
            return
        self.ensure_token()

        group_id = random.choice(TEST_GROUP_IDS)
        self.client.put(
            f"/api/v1/groups/{group_id}",
            json={
                "description": f"Updated by locust {random.randint(0,1000)}"
            },
            name="groups/update",
        )

# -------------------------------------------------------------------
# Engine Service Users
# -------------------------------------------------------------------

class EngineServiceUser(AuthenticatedUser):
    host = ENGINE_SERVICE_URL
    wait_time = between(1, 2)

    @task(3)
    def list_and_resolve_layouts(self):
        self.ensure_token()
        self.client.get(
            f"/api/v1/layouts/by-schema/{SCHEMA_ID}",
            name="layouts/list",
        )
        self.client.get(
            f"/api/v1/layouts/resolve/{SCHEMA_ID}",
            name="layouts/resolve",
        )

    @task(2)
    def update_existing_layout(self):
        if not TEST_LAYOUT_IDS:
            return
        self.ensure_token()

        layout_id = random.choice(TEST_LAYOUT_IDS)
        self.client.put(
            f"/api/v1/layouts/{layout_id}",
            json={
                "definition": [
                    {
                        "type": "field",
                        "field_name": "updated_field",
                        "label": f"Updated {random.randint(0,1000)}",
                    }
                ]
            },
            name="layouts/update",
        )
