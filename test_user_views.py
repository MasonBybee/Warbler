"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


from unittest import TestCase
from models import db, Message, User
from app import app, CURR_USER_KEY, session, g
import unittest


app.config["TESTING"] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
app.config["WTF_CSRF_ENABLED"] = False
app.config["SQLALCHEMY_ECHO"] = False


class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()
        db.session.begin_nested()
        self.testuser = User.signup(
            username="testUser",
            email="testuser@test.com",
            password="password",
            image_url=None,
        )
        db.session.commit()

    def tearDown(self):
        with app.test_request_context():
            session.clear()
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home(self):
        with app.test_client() as self.client:
            """Tests users home view"""
            # test with no user logged in
            resp = self.client.get("/", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"<h4>New to Warbler?</h4>", resp.data)

            # test with logged in user
            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get("/", follow_redirects=True)
            testHtml = bytes(f"<p>@{self.testuser.username}</p>", encoding="utf-8")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(testHtml, resp.data)

    def test_signup(self):
        with app.test_client() as self.client:
            # test with no user logged in

            resp = self.client.get("/signup", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<h2 class="join-message">Join Warbler today.</h2>', resp.data
            )

            # test with logged in user
            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get("/signup", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<div class="alert alert-danger">You are already logged in!</div>',
                resp.data,
            )

    def test_login(self):
        with app.test_client() as self.client:
            # test with no user logged in

            resp = self.client.get("/login", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'<h2 class="join-message">Welcome back.</h2>', resp.data)

            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get("/login", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<div class="alert alert-danger">You are already logged in!</div>',
                resp.data,
            )

    def test_logout(self):
        with app.test_client() as self.client:
            # test with no user logged in

            resp = self.client.get("/logout", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<div class="alert alert-danger">You do not have access to this page</div>',
                resp.data,
            )

            # test with logged in user
            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get("/logout", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"<h4>New to Warbler?</h4>", resp.data)

    def test_list_users(self):
        with app.test_client() as self.client:
            # test with no user logged in

            resp = self.client.get("/users", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"<p>@testUser</p>", resp.data)

    def test_user_profiles(self):
        with app.test_client() as self.client:
            # test with no user logged in
            u = User.signup(
                email="testing@test.com",
                username="TestUser2",
                password="HASHED_PASSWORD",
                image_url=None,
            )

            db.session.add(u)
            db.session.commit()
            resp = self.client.get(f"/users/{u.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<h4 id="sidebar-username">@TestUser2</h4>',
                resp.data,
            )
            self.assertNotIn(
                b'<button class="btn btn-outline-primary">Follow</button>', resp.data
            )

            # test with logged in user
            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get(f"/users/{u.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<h4 id="sidebar-username">@TestUser2</h4>',
                resp.data,
            )
            self.assertIn(
                b'<button class="btn btn-outline-primary">Follow</button>', resp.data
            )

    def test_user_followers(self):
        with app.test_client() as self.client:
            # test with no user logged in
            u = User.signup(
                email="testing@test.com",
                username="TestUser2",
                password="HASHED_PASSWORD",
                image_url=None,
            )

            db.session.add(u)
            self.testuser.followers.append(u)
            db.session.commit()
            resp = self.client.get(
                f"/users/{self.testuser.id}/followers", follow_redirects=True
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<div class="alert alert-danger">Access unauthorized.</div>',
                resp.data,
            )

            # test with logged in user
            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get(
                f"/users/{self.testuser.id}/followers", follow_redirects=True
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b"<p>@TestUser2</p>",
                resp.data,
            )

    def test_user_following(self):
        with app.test_client() as self.client:
            # test with no user logged in
            u = User.signup(
                email="testing@test.com",
                username="TestUser2",
                password="HASHED_PASSWORD",
                image_url=None,
            )

            db.session.add(u)
            u.followers.append(self.testuser)
            db.session.commit()
            resp = self.client.get(
                f"/users/{self.testuser.id}/following", follow_redirects=True
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b'<div class="alert alert-danger">Access unauthorized.</div>',
                resp.data,
            )

            # test with logged in user
            with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = self.client.get(
                f"/users/{self.testuser.id}/following", follow_redirects=True
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                b"<p>@TestUser2</p>",
                resp.data,
            )
