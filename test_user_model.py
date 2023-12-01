"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from unittest import TestCase
import unittest
from app import app
from models import db, User, Message, Follows


app.config["SQLALCHEMY_ECHO"] = False
app.config["TESTING"] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()
        db.session.begin_nested()
        self.test_user_email = f"test{unittest.TestCase.id(self)}@test.com"
        self.test_username = f"testuser{unittest.TestCase.id(self)}"
        self.testuser = User.signup(
            username=self.test_username,
            email=self.test_user_email,
            password="userPassword",
            image_url=None,
        )
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        with app.test_client() as self.client:
            """Does basic model work?"""

            u = User(
                email="testing@test.com",
                username="TestUser",
                password="HASHED_PASSWORD",
            )

            db.session.add(u)
            db.session.commit()
            users = User.query.all()

            # User should have no messages & no followers
            self.assertEqual(len(users), 2)
            self.assertEqual(len(u.messages), 0)
            self.assertEqual(len(u.followers), 0)

    def test_user_follows(self):
        with app.test_client() as self.client:
            u = User.signup(
                username="TestUser",
                email="testuser@test.com",
                password="password",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/2048px-Default_pfp.svg.png",
            )
            self.testuser.following.append(u)
            db.session.commit()

            self.assertFalse(self.testuser.is_followed_by(u))
            self.assertTrue(self.testuser.is_following(u))

            self.testuser.following.remove(u)
            u.following.append(self.testuser)
            db.session.commit()

            self.assertFalse(u.is_followed_by(self.testuser))
            self.assertTrue(u.is_following(self.testuser))

    def test_user_signup(self):
        with app.test_client() as self.client:
            u = User.signup(
                username="TestUser",
                email="testuser@test.com",
                password="password",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/2048px-Default_pfp.svg.png",
            )
            db.session.commit()
            self.assertIsInstance(u, User)
            self.assertNotEqual(u.password, "password")
            self.assertGreater(len(u.password), 8)

            u2 = User.signup(
                username="TestUser2",
                email="testuser@test.com",
                password="password",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/2048px-Default_pfp.svg.png",
            )
            self.assertFalse(u2)

    def test_user_authenticate(self):
        with app.test_client() as self.client:
            u = User.signup(
                username="TestUser",
                email="testuser@test.com",
                password="password",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/2048px-Default_pfp.svg.png",
            )
            db.session.commit()
            valid_user = User.authenticate(username="TestUser", password="password")
            invalid_username = User.authenticate(
                username="UserTest", password="password"
            )
            invalid_passoword = User.authenticate(
                username="TestUser", password="wordpass"
            )
            self.assertEqual(u, valid_user)
            self.assertFalse(invalid_username)
            self.assertFalse(invalid_passoword)
