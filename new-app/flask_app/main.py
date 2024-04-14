# Main.py
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app


main = Blueprint('main', __name__)
index = None



@main.route("/", methods=["GET", "POST"])
def home():
    return render_template("../templates/base.html")


@main.route("/admin", methods=["GET", "POST"])
def admin_page():
    return render_template("admin.html")



@main.route("/search", methods=["GET", "POST"])
def search_api():
    query = request.args.get("query", "")
    if not index:
        return jsonify({"error": "Search index is not available."}), 503
    results = index.search(query)
    return jsonify(results)