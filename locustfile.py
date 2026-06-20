from locust import HttpUser, between, task


class SkillBridgeUser(HttpUser):
    wait_time = between(1, 2)
    token = None

    def on_start(self):
        import uuid
        email = f"load_{uuid.uuid4().hex[:8]}@test.com"
        self.client.post("/auth/register", json={
            "email": email,
            "password": "Test@1234",
            "full_name": "Load Test User",
            "role": "client",
        })
        response = self.client.post("/auth/login", json={
            "email": email,
            "password": "Test@1234",
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.token}"

    @task(5)
    def browse_providers(self):
        self.client.get("/providers")

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(2)
    def get_my_requests(self):
        if self.token:
            self.client.get("/requests")