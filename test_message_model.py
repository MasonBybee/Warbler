"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


from unittest import TestCase
import unittest
from app import app, CURR_USER_KEY
from models import db, User, Message, Follows


app.config["SQLALCHEMY_ECHO"] = False
app.config["TESTING"] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]


class MessageModelTestCase(TestCase):
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

    def test_message_model(self):
        with app.test_client() as self.client:
            msg = Message(text="testmessage", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()
            self.assertIsInstance(msg, Message)
            self.assertEqual(self.testuser, msg.user)
