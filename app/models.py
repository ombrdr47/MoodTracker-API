from collections import OrderedDict
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

STR_DATE_FRMT = "%b %d %Y %H:%M:%S"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(258))
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    moods = db.relationship("MoodEntry", backref="user", lazy="dynamic")

    def set_password(self, password):
        """Converts user provided password to a SHA256 hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies that user provided password matches hashed password."""
        return check_password_hash(self.password_hash, password)

    def update_streaks(self, method_type):
        """Updates current streak for a user using timestamps from mood entries."""
        try:
            latest_entry = self._get_latest_entry()

            if method_type == "GET":
                self._update_current_streak_on_get(latest_entry)

            elif method_type == "POST":
                self._update_current_streak_on_post(latest_entry)

        except Exception as e:
            # Handle database query exceptions or other unexpected errors
            # Log the error for further investigation
            print(f"Error in update_streaks: {e}")

    def _get_latest_entry(self):
        return (
            db.session.query(MoodEntry)
            .filter(MoodEntry.user_id == self.id)
            .order_by(MoodEntry.timestamp.desc())
            .first()
        )

    def _update_current_streak_on_get(self, latest_entry):
        if latest_entry:
            latest_entry_ts = latest_entry.timestamp
        else:
            latest_entry_ts = datetime.utcnow()

        if _check_should_update(latest_entry_ts) == "Reset":
            self.current_streak = 0

    def _update_current_streak_on_post(self, latest_entry):
        if latest_entry:
            latest_entry_ts = latest_entry.timestamp
        else:
            latest_entry_ts = None

        most_recent_post = _check_should_update(latest_entry_ts)

        if most_recent_post == "Yesterday":
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        elif most_recent_post == "Reset":
            self.current_streak = 0

    def get_current_streak(self):
        """Return current user streak"""
        return self.current_streak

    def get_best_streak(self):
        """Return best user streak all time"""
        return self.best_streak

    def asdict(self):
        """Returns instance of dict to represent User object."""
        return OrderedDict(
            id=self.id,
            username=self.username,
            email=self.email,
            current_streak=self.current_streak,
            best_streak=self.best_streak,
        )

    def __repr__(self):
        """Returns instance of string to represent User object."""
        return "<User {}>".format(self.username)

@login.user_loader
def load_user(id):
    """Saves session data about current_user flask-login."""
    return User.query.get(int(id))

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    mood_score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    def asdict(self):
        return OrderedDict(
            id=self.id,
            user_id=self.user_id,
            mood_score=self.mood_score,
            timestamp=(self.timestamp.strftime(STR_DATE_FRMT)),
        )

    def get_timestamp(self):
        """Returns unix timestamp for mood entry"""
        return self.timestamp

    def __repr__(self):
        """Returns instance of string to represent MoodEntry object."""
        return "<MoodEntry Score:{} Time:{}>".format(self.mood_score, self.timestamp)

def _check_should_update(latest_entry_ts):
    """A users streak should be modified if a POST request is made on
    the day immediately following the most recent post, or if a GET request
    is made that shows the latest post being more than a day prior."""
    if not latest_entry_ts:
        return "Yesterday"

    today = datetime.utcnow().date()
    latest_post_day = latest_entry_ts.date()

    if today == latest_post_day:
        return "Today"

    if today - timedelta(days=1) == latest_post_day:
        return "Yesterday"

    return "Reset"
