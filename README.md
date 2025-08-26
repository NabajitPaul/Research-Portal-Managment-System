# Research-Portal-Managment-System (RPMS )

![GitHub repo size](https://img.shields.io/github/repo-size/your-username/research-portal-management-system)
![GitHub stars](https://img.shields.io/github/stars/your-username/research-portal-management-system?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/research-portal-management-system?style=social)
![License](https://img.shields.io/github/license/your-username/research-portal-management-system)


🚀Overview

The **Research Portal Management System (RPMS)** is a centralized academic profile management platform powered by **Flask (Python)** and integrated with **[ORCID](https://orcid.org/)**.  
It enables researchers to maintain up-to-date profiles by automatically fetching their **publications, citations, and research data** via ORCID, ensuring accuracy while reducing manual effort.  

This system is designed for **universities, research institutions, and independent researchers** to manage and showcase research output in a structured manner.

✨Key Features

- 🔗 **ORCID Integration** – Fetch and sync publications, citations, and research metadata.  
- 👤 **Researcher Profiles** – Personalized dashboards with publication history & academic details.  
- 🔍 **Search & Discovery** – Explore researchers, projects, and publications with filters.  
- 🛠 **Admin Panel** – Tools for institutions to manage researcher data and verify profiles.  

🛠 Tech Stack

**Backend:**  
- Python (Flask)  
- ORCID Public API Integration  
- SQLAlchemy ORM  

**Frontend:**  
- HTML5, CSS3, JavaScript  
- TailwindCSS  

**Database:**  
- PostgreSQL / MySQL / SQLite (depending on environment)  

**Other Tools:**  
- Flask-JWT / OAuth2.0 for authentication  
- Gunicorn / uWSGI (for production deployment)  
- Docker (for containerization)  
- Git & GitHub (version control)  

📦 Installation & Setup

Clone the repository:

git clone https://github.com/your-username/research-portal-management-system.git
cd research-portal-management-system


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # for Linux/Mac
venv\Scripts\activate     # for Windows


Install dependencies:

pip install -r requirements.txt


Set up environment variables in a .env file:

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
ORCID_CLIENT_ID=your_orcid_client_id
ORCID_CLIENT_SECRET=your_orcid_secret

Run the Flask server:

python app.py



🔬 Future Enhancements

📊 Advanced analytics (h-index, impact factor, citation metrics).
🤝 Research collaboration and networking features.
🗂 Institution-wide repositories of publications.
🌐 API endpoints for third-party integrations.
