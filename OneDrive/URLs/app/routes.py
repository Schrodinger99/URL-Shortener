from flask import render_template, redirect, url_for, flash, request, jsonify
from . import db, create_app
from .models import User, Link, Click
from flask_login import login_user, logout_user,login_required, current_user
from .utils import generate_short_url, generate_csv_report, get_geo_info
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method = 'sha256')
        new_user = User(email = email, username = username, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    links = Link.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', links=links)

@app.route('/create_link', methods=['POST'])
@login_required
def create_link():
    original_url = request.form['original_url']
    short_url = generate_short_url()
    new_link = Link(original_url=original_url, short_url=short_url, user_id=current_user.id)
    db.session.add(new_link)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    link.clicks += 1

    # Registrar click con detalles
    click = Click(
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        country=get_geo_info(request.remote_addr),
        link_id=link.id
    )
    db.session.add(click)
    db.session.commit()
    
    return redirect(link.original_url)

@app.route('/download_report')
@login_required
def download_report():
    links = Link.query.filter_by(user_id=current_user.id).all()
    report_path = generate_csv_report(links)
    return redirect(url_for('static', filename='reports/' + os.path.basename(report_path)))

@app.route('/stats/<int:link_id>')
@login_required
def stats(link_id):
    link = Link.query.get_or_404(link_id)
    if link.user_id != current_user.id and not current_user.is_admin:
        return redirect(url_for('dashboard'))
    clicks = Click.query.filter_by(link_id=link_id).all()
    return render_template('stats.html', link=link, clicks=clicks)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))