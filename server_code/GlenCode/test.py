import anvil.users
import random

DOMAINS = ["test.com", "mock.io", "demo.org", "example.dev"]

def generate_email(name):
  username = name.lower().replace(" ", ".")
  return f"{username}{random.randint(10,99)}@{random.choice(DOMAINS)}"

@anvil.server.callable
def create_mock_users():
  names = [
    "Michael Lee", "Sarah Lim", "Aisha Nur",
  ]

  created = []
  for n in names:
    email = generate_email(n)
    password = "glendonglendon"  # same password for all mocks
    user = anvil.users.signup_with_email(email, password, remember=False)
    user['full_name'] = n
    user['role'] = random.choice(["Admin", "Staff"])
    created.append(email)

    return created
