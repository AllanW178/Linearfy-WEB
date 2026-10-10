## GitHub development history and what changed

My GitHub commit titles are sometimes short because several uploads and file clean-ups were made through GitHub’s web interface. This section explains the purpose and outcome of those commits in more detail.

### 4 September 2026 - project setup and dependency management

I created the `requirements.txt` file so the project dependencies could be installed consistently on another computer. I also created a backup requirements file while resolving the correct package setup. After confirming the final dependency list, I removed duplicate and unnecessary versions. This made the setup process clearer and reduced confusion about which libraries Linearfy requires: Flask, Flask-Bcrypt, and Flask-SQLAlchemy.

I also updated the README during this stage so the installation instructions matched the project files.

### 14 September 2026 - first complete project upload

I uploaded the main Linearfy website files, including the Flask application, templates, CSS, JavaScript, and product images. This established the working base version of the project in GitHub.

The uploaded application included the main shopping experience: product browsing, user registration and login, shopping cart functionality, database storage, and a shared page layout. This meant later changes could be compared against a stable starting point rather than being added as one large final upload.

### 23 September 2026 - improving the application and cleaning the repository

I updated `app.py` to improve the functionality and reliability of the Flask application. This development stage included improvements to areas such as stock handling, user and administrator permissions, seller listings, moderation, and database-connected features.

I removed an old website folder after replacing it with the current Linearfy structure. This prevented two versions of the project from being stored in the same repository and made it clearer which files were current.

I also removed `linearfy.db` from GitHub. The database file is generated locally when the application runs, so storing it in the repository could expose test account data and makes the repository less portable. The code, database models, and sample-product setup remain in the project, allowing the database to be recreated.

Finally, I updated the README to remove obsolete download instructions. This ensured that the documentation described the current project structure instead of an earlier version.

### 9 October 2026 - final structure, documentation, and assessment evidence

I reorganised the project files by removing an outdated Linearfy directory and uploading the final project structure. This made the repository easier to navigate and ensured that the current application files, templates, static files, and images were available in one clear location.

I replaced the earlier README with a detailed version that explains the project purpose, target users, technologies, database structure, security measures, testing, relevant implications, and iterative improvements. This documentation provides evidence of how Linearfy developed through planning, testing, feedback, and refinement.

### How testing influenced the development

The most important improvement came from testing stock control. At first, limiting the quantity controls in the browser appeared sufficient. However, further testing showed that stock could change after an item had already been placed in the cart. I improved the application by adding a second stock check on the Flask server during checkout. This prevents an order from being completed if the requested quantity is no longer available, and prevents negative stock values.

Other refinements included preventing duplicate wishlist entries through a database constraint, adding administrator-only access checks, creating a seller listing and moderation workflow, validating submitted data, and giving users clearer status feedback through notifications and stock indicators. These changes show that the final outcome was improved in response to testing rather than being created in one step.
