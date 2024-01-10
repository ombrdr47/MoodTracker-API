from flask import jsonify, current_app
from app import app, db

def generate_error_response(error, status_code):
    return jsonify({"errors": {error.name: error.description}}), status_code

@app.errorhandler(400)
def handle_bad_request_error(error):
    return generate_error_response(error, 400)

@app.errorhandler(401)
def handle_unauthorized_error(error):
    return generate_error_response(error, 401)

@app.errorhandler(404)
def handle_not_found_error(error):
    return generate_error_response(error, 404)

@app.errorhandler(422)
def handle_validation_error(error):
    exc = error.exc
    return jsonify({"errors": exc.messages}), 422

@app.errorhandler(500)
def handle_internal_error(error):
    db.session.rollback()
    current_app.logger.error("An unexpected error occurred:", exc_info=True)
    return generate_error_response(error, 500)
