from fastapi_sso.sso.google import GoogleSSO
from starlette.middleware.sessions import SessionMiddleware  # Updated import
import yaml

class GoogleSSOManager:
    def __init__(self, app, config_path: str, callback_url: str = None):
        """
        Initialize Google SSO with configuration from a YAML file
        and set up session middleware for the FastAPI app.
        """
        self.config = self._load_config(config_path)
        if callback_url is None:
            callback_url = self.config["google_sso"]["callback_url"]
            
        self.google_sso = GoogleSSO(
            client_id=self.config["google_sso"]["client_id"],
            client_secret=self.config["google_sso"]["client_secret"],
            redirect_uri=callback_url
        )

        # Add SessionMiddleware to the app
        app.add_middleware(SessionMiddleware, secret_key=self.config["google_sso"].get("secret_key", "default_secret_key"))

    def _load_config(self, config_path: str) -> dict:
        """Load the SSO configuration from a YAML file."""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def get_login_redirect(self):
        """Generate the login URL for Google SSO."""
        return self.google_sso.get_login_redirect()

    async def verify_and_process(self, request):
        """Verify and process the Google SSO callback."""
        return await self.google_sso.verify_and_process(request)