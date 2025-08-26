document.addEventListener('DOMContentLoaded', function() {
    // --- Form Validations (Client-side examples) ---
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            const password = document.getElementById('password').value;
            const orcidId = document.getElementById('orcid_id').value;
            
            if (password.length < 6) {
                alert('Password must be at least 6 characters long.');
                event.preventDefault();
                return;
            }

            // Basic ORCID ID format check (more robust check done server-side)
            const orcidPattern = /^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/;
            if (!orcidPattern.test(orcidId)) {
                alert('Invalid ORCID ID format. Expected: 0000-0001-2345-6789');
                event.preventDefault();
                return;
            }
        });
    }

    // --- Dynamic Publication Name Label for Paper Upload ---
    const categorySelect = document.getElementById('category');
    const publicationNameLabel = document.getElementById('publication_name_label');
    const publicationNameInput = document.getElementById('publication_name');

    if (categorySelect && publicationNameLabel && publicationNameInput) {
        categorySelect.addEventListener('change', function() {
            const selectedCategory = this.value;
            let labelText = "Name of ";
            let placeholderText = "Enter name";

            if (selectedCategory === "Journal") {
                labelText += "Journal:";
                placeholderText = "e.g., Nature Communications";
            } else if (selectedCategory === "Conference") {
                labelText += "Conference:";
                placeholderText = "e.g., International Conference on Machine Learning";
            } else if (selectedCategory === "Book Chapter") {
                labelText += "Book:";
                placeholderText = "e.g., Deep Learning by Goodfellow, Bengio, Courville";
            } else {
                labelText = "Name of Journal/Conference/Book:";
                placeholderText = "Select category first";
            }
            publicationNameLabel.textContent = labelText;
            publicationNameInput.placeholder = placeholderText;
        });
    }

    // Example: Client-side validation for paper upload form
    const uploadPaperForm = document.getElementById('uploadPaperForm');
    if (uploadPaperForm) {
        uploadPaperForm.addEventListener('submit', function(event) {
            const title = document.getElementById('title').value.trim();
            const author = document.getElementById('author_name').value.trim();
            const category = document.getElementById('category').value;
            const pubName = document.getElementById('publication_name').value.trim();
            const pubDate = document.getElementById('publication_date').value;
            const fileInput = document.getElementById('file');

            if (!title || !author || !category || !pubName || !pubDate) {
                alert('Please fill in all paper details.');
                event.preventDefault();
                return;
            }
            if (fileInput.files.length === 0) {
                alert('Please select a file to upload.');
                event.preventDefault();
                return;
            }
        });
    }

});