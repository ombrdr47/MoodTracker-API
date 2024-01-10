from flask_login import current_user
from app import db
from app.models import User

def calculate_streak_percentile():
    """
    Returns the percentile rank of the current user's best_streak.
    
    Queries 3 integer values from the database and passes them to the
    percentileofscore helper.
    
    Returns:
        The percentile rank of the current user's best_streak.
        Returns None if there is an error during the calculation.
    """
    try:
        score = current_user.best_streak
        lower_values = db.session.query(User.best_streak).filter(User.best_streak < score).count()
        equal_values = db.session.query(User.best_streak).filter(User.best_streak == score).count()
        total_users = db.session.query(User).count()

        percentile_rank = calculate_percentile(lower_values, equal_values, total_users)
        return percentile_rank
    except Exception as e:
        # Handle database query exceptions or other unexpected errors
        # Log the error for further investigation
        print(f"Error in calculate_streak_percentile: {e}")
        return None

def calculate_percentile(lower_values, equal_values, total_users):
    """
    Calculate the percentile rank using the formula: PR = (L + (S / 2)) / N.

    Parameters:
        lower_values (int): Number of values lower than the current user's best_streak.
        equal_values (int): Number of values equal to the current user's best_streak.
        total_users (int): Total number of users in the database.

    Returns:
        The percentile rank as a decimal value.
        Returns None if there is an error during the calculation.
    """
    try:
        percentile_decimal = (lower_values + (equal_values / 2)) / total_users
        return round(percentile_decimal, 2) * 100
    except ZeroDivisionError:
        # Handle the case where total_users is 0 to avoid division by zero
        return None
