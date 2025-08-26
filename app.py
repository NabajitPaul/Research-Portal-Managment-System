import os
# import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash , jsonify
from werkzeug.utils import secure_filename
from functools import wraps

from models import db, User, Paper, OrcidWork
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# --- Helper Functions ---

def fetch_orcid_public_data(orcid_id):
    """Fetches public works data from ORCID API."""
    works_data = []
    name_info = {"given_name": "N/A", "family_name": "N/A"}
    
    if not orcid_id or not (orcid_id.count('-') == 3 and len(orcid_id) == 19): # Basic ORCID format check
        return None, None # Indicate invalid ORCID

    # Fetch personal details (like name)
    person_url = f"{app.config['ORCID_API_BASE_URL']}{orcid_id}/person"
    headers = {'Accept': 'application/json'}
    try:
        person_response = requests.get(person_url, headers=headers, timeout=10)
        person_response.raise_for_status() # Raises an exception for bad status codes
        person_json = person_response.json()
        
        # name_data = person_json.get('name', {})
        # if name_data:
        #     given_names = name_data.get('given-names', {}).get('value')
        #     family_name = name_data.get('family-name', {}).get('value')
        #     if given_names: name_info["given_name"] = given_names
        #     if family_name: name_info["family_name"] = family_name
          # Safely extract name information
        name_details_obj = person_json.get('name') # Get the 'name' object, could be None or a dict
        
        if name_details_obj and isinstance(name_details_obj, dict):
            # Process given-names
            given_names_struct = name_details_obj.get('given-names') # This is the {"value": "Name"} part or None
            if given_names_struct and isinstance(given_names_struct, dict):
                val = given_names_struct.get('value')
                if val: # Ensure value is not None or empty
                    name_info["given_name"] = val
            
            # Process family-name
            family_name_struct = name_details_obj.get('family-name') # This is the {"value": "Name"} part or None
            if family_name_struct and isinstance(family_name_struct, dict):
                val = family_name_struct.get('value')
                if val: # Ensure value is not None or empty
                    name_info["family_name"] = val
        # If name_details_obj is None or not a dict, name_info will keep its default "N/A" values.

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching ORCID person data for {orcid_id}: {e}")
        # Continue to fetch works even if name fails, or handle as critical error

    # Fetch works
    works_url = f"{app.config['ORCID_API_BASE_URL']}{orcid_id}/works"
    try:
        works_response = requests.get(works_url, headers=headers, timeout=15)
        works_response.raise_for_status()
        works_json = works_response.json()

        for group in works_json.get('group', []):
            for summary in group.get('work-summary', []):
                title_info = summary.get('title', {}).get('title', {}).get('value', 'No Title')
                work_type = summary.get('type', 'N/A')
               
                publication_date_data_from_summary = summary.get('publication-date')
                pub_date = publication_date_data_from_summary if publication_date_data_from_summary is not None else {}

                year = 'N/A'
                year_details = pub_date.get('year') 
                if year_details and isinstance(year_details, dict):
                    year_value_candidate = year_details.get('value')
                    if year_value_candidate is not None:
                        year = year_value_candidate
                
                journal_title_obj = summary.get('journal-title') 
                journal = journal_title_obj.get('value') if journal_title_obj and isinstance(journal_title_obj, dict) else 'N/A'
                
                put_code = str(summary.get('put-code', 'N/A'))

                doi = None
                external_ids_data = summary.get('external-ids', {}) 
                if external_ids_data: 
                    external_ids_list = external_ids_data.get('external-id', [])
                    for ext_id in external_ids_list:
                        if ext_id and ext_id.get('external-id-type') == 'doi': 
                            doi = ext_id.get('external-id-value')
                            break
                
                works_data.append({
                    'put_code': put_code,
                    'title': title_info,
                    'work_type': work_type,
                    'publication_year': year,
                    'journal_title': journal,
                    'doi': doi
                })
        return name_info, works_data
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching ORCID works data for {orcid_id}: {e}")
        return name_info, []

def store_orcid_data(user_id, works_data):
    """Stores or updates ORCID works in the database."""
    OrcidWork.query.filter_by(user_id=user_id).delete()
    
    for work_item in works_data:
        new_work = OrcidWork(
            user_id=user_id,
            put_code=work_item.get('put_code'),
            title=work_item.get('title'),
            work_type=work_item.get('work_type'),
            publication_year=work_item.get('publication_year'),
            journal_title=work_item.get('journal_title'),
            doi=work_item.get('doi')
        )
        db.session.add(new_work)
    db.session.commit()

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('username') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    # Always redirect to the login page when the root URL is accessed.
    # The login page will then handle authentication.
    # If a user is already logged in (session exists) and tries to access other protected routes,
    # the @login_required or @admin_required decorators will still work as intended.
    # If a logged-in user happens to navigate to /login, they will see the login form again.
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        orcid_id = request.form['orcid_id']
        user_type = request.form['user_type']

        if not all([username, email, password, orcid_id, user_type]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or Email already exists.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(orcid_id=orcid_id).first():
            flash('This ORCID ID is already registered.', 'danger')
            return redirect(url_for('register'))

        name_info, orcid_works = fetch_orcid_public_data(orcid_id)

        if name_info is None and orcid_works is None: 
            flash('Invalid ORCID ID format. It should be like 0000-0001-2345-6789.', 'danger')
            return redirect(url_for('register'))
        
        if not orcid_works and name_info and name_info.get("given_name") == "N/A": 
             flash(f'Could not fetch data for ORCID ID {orcid_id}. Please ensure it is a valid and public profile.', 'warning')

        new_user = User(username=username, email=email, orcid_id=orcid_id, user_type=user_type)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit() 

        if orcid_works:
            store_orcid_data(new_user.id, orcid_works)
        
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['user_type'] = new_user.user_type
        flash('Registration successful! Your ORCID data has been fetched.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If a user is already logged in and somehow navigates to /login,
    # they will see the login form again. This is often the desired behavior
    # if the root ('/') must always show login first.
    # Alternatively, you could redirect them if already logged in:
    # if 'user_id' in session:
    #     if session.get('username') == 'admin':
    #         return redirect(url_for('admin_dashboard'))
    #     return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        orcid_id_optional = request.form.get('orcid_id_optional', '').strip() 

        if username == 'admin' and password == 'admin123':
            session['user_id'] = 0 
            session['username'] = 'admin'
            session['user_type'] = 'Admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            
            current_orcid_id_to_use = orcid_id_optional if orcid_id_optional else user.orcid_id

            if current_orcid_id_to_use:
                if orcid_id_optional and orcid_id_optional != user.orcid_id:
                    existing_orcid_user = User.query.filter(User.orcid_id == orcid_id_optional, User.id != user.id).first()
                    if existing_orcid_user:
                        flash('The provided ORCID ID is already associated with another account.', 'danger')
                    else:
                        user.orcid_id = orcid_id_optional 
                        db.session.commit()
                        flash('Your ORCID ID has been updated.', 'info')
                
                name_info, orcid_works = fetch_orcid_public_data(user.orcid_id) 
                if orcid_works:
                    store_orcid_data(user.id, orcid_works)
                    flash('Your ORCID data has been updated.', 'success')
                elif name_info is None and orcid_works is None:
                     flash('Invalid ORCID ID format provided for update.', 'warning')
                elif not orcid_works:
                    flash(f'Could not fetch new data for ORCID ID {user.orcid_id}. Displaying previously stored data.', 'warning')
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('logout'))
        
    orcid_works = OrcidWork.query.filter_by(user_id=user.id).all()
    uploaded_papers = Paper.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, orcid_works=orcid_works, uploaded_papers=uploaded_papers)

@app.route('/upload_paper', methods=['POST'])
@login_required
def upload_paper():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))

    title = request.form['title']
    author_name = request.form['author_name'] 
    category = request.form['category']
    publication_name = request.form['publication_name']
    publication_date_str = request.form['publication_date']

    if not all([title, author_name, category, publication_name, publication_date_str, file]):
        flash('All fields for paper upload are required.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
        return redirect(url_for('dashboard'))

    if file:
        filename = secure_filename(file.filename)
        user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
        os.makedirs(user_upload_dir, exist_ok=True)
        file_path = os.path.join(user_upload_dir, filename)
        
        try:
            file.save(file_path)
            
            new_paper = Paper(
                title=title,
                author_name=author_name,
                category=category,
                publication_name=publication_name,
                publication_date=publication_date,
                file_path=file_path, 
                user_id=session['user_id']
            )
            db.session.add(new_paper)
            db.session.commit()
            flash('Paper uploaded successfully!', 'success')
        except Exception as e:
            app.logger.error(f"File save or DB error: {e}")
            flash('An error occurred during file upload or saving data.', 'danger')

    return redirect(url_for('dashboard'))


@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    total_users = User.query.filter(User.username != 'admin').count()
    
    all_selectable_users = User.query.filter(User.username != 'admin').order_by(User.username).all()

    selected_user_id = request.args.get('selected_user_id', type=int)
    selected_user_details = None
    user_papers = []
    user_orcid_works = []

    if selected_user_id:
        selected_user = User.query.get(selected_user_id)
        if selected_user and selected_user.username != 'admin': 
            selected_user_details = selected_user
            user_papers = Paper.query.filter_by(user_id=selected_user_id).all()
            user_orcid_works = OrcidWork.query.filter_by(user_id=selected_user_id).all()
        else:
            flash("Selected user not found or is invalid.", "warning")

    return render_template('admin_dashboard.html', 
                           total_users=total_users,
                           all_selectable_users=all_selectable_users,
                           selected_user_details=selected_user_details,
                           user_papers=user_papers,
                           user_orcid_works=user_orcid_works)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- CLI command to create tables ---
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    with app.app_context():
        db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)