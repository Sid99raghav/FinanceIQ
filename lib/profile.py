import os
import json

BASE_DIR = os.path.join(os.getcwd(), "user_profiles")  # Updated directory name

# Ensure the base directory exists
os.makedirs(BASE_DIR, exist_ok=True)

class UserProfile:
    def __init__(self, email_id):
        self.email_id = email_id
        self.user_dir = os.path.join(BASE_DIR, email_id)
        os.makedirs(self.user_dir, exist_ok=True)
        self.profile_path = os.path.join(self.user_dir, "profile.json")
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r") as file:
                return json.load(file)
        # Add default theme
        return {"role": "", "grade": "", "theme": "default"}

    def save(self):
        with open(self.profile_path, "w") as file:
            json.dump(self.data, file, indent=4)

    def update(self, updates):
        self.data.update(updates)
        self.save()
        return self.data

    def get(self):
        return self.data

# Backward-compatible functions

def get_profile_path(email_id):
    """Generate the file path for the user's profile JSON."""
    user_dir = os.path.join(BASE_DIR, email_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "profile.json")

def save_profile(email_id, profile_data):
    """Save the profile data to a JSON file."""
    profile = UserProfile(email_id)
    profile.data = profile_data
    profile.save()

def load_profile(email_id):
    """Load the profile data from the JSON file."""
    profile = UserProfile(email_id)
    return profile.get()

def update_profile(email_id, updates):
    """Update specific fields in the user's profile."""
    profile = UserProfile(email_id)
    return profile.update(updates)
