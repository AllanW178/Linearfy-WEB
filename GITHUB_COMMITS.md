## GitHub development history and what changed

Some of my commits to GitHub have been short due to multiple file clean ups and uploads being completed via the GitHub website. I will detail the purpose and result of these commits here.

### 10 August 2026 - initial interface build and visual experimentation

This was the first major interface-development stage of Linearfy. I created and updated the main page templates, including the shared `base.html` layout, cart page, account page, administrator page, account-editing page, and custom 404 page. Building these pages separately allowed me to develop the website as smaller components instead of attempting to create the whole site in one change.

I also updated `style.css` and `main.js` to improve the appearance and interaction of the pages. The shared stylesheet helped keep spacing, colours, typography, buttons, navigation, and product cards consistent across the application. JavaScript was used to improve user feedback and page interaction.

During this stage, I created `three-bg.js` and later updated it as an experiment with a more visually interesting background. I checked how the visual effect interacted with the text, cards, and navigation so that the interface remained readable. This was part of exploring how to make the store feel more polished while still keeping the shopping content easy to use.

The custom 404 page was added so that users who enter an invalid address do not see a generic browser error. Instead, they are given a clear explanation and a way to return to the website. The account and administrator page updates were also important because they separated normal user tasks from administrator-only management tasks.

### 17 August 2026 - refinement, documentation, and removing unused planning material

I updated the background script again after reviewing its effect on the layout. This was a refinement stage: I adjusted the visual work after seeing how it fitted with the rest of the website rather than treating the first version as final.

I removed the earlier “Plans for The Website” file once its planning information had been replaced by the working application, testing evidence, and more relevant documentation. Removing outdated planning material made the repository easier to understand and reduced the chance that someone would mistake an early plan for the completed outcome.

I also updated the README several times during this period. The documentation was improved as the project changed, so it could explain the current version of Linearfy rather than describing features or plans that were no longer accurate.

## 4 September 2026 - project setup and dependency management
This commit provided a requirements file so another user could install the project dependencies into their system in the same way. I created a backup requirements file whilst also resolving the required packages for the project. I then inspected the list of required packages and removed any redundant packages and versions. This helped clarify which packages Linearfy requires (Flask, Flask-Bcrypt, Flask-SQLAlchemy) and simplified the installation process.

I also updated the README so that the installation process was in sync with the project files.

## 14 September 2026 - first complete project upload
This commit contained the files required for the main Linearfy site (javascript, CSS, product images, templates and the Flask app). This provided a working version of the project on GitHub.

The app included user registration and login, a shopping cart, a shared layout page, database persistence, browsing products and seller management. This provided a stable version of the project for future code to be compared against rather than having all changes in a single final commit.

## 23 September 2026 - improving the application and cleaning the repository
This commit also involved making changes to the Flask app in app.py to increase the reliability and functionality of the app. This included changes to admin and user roles, moderation and seller management, database functionality and stock control.

This commit involved removing an old website directory in favour of the current Linearfy site. This avoided two separate versions of the project being present within the same repository and provided clarity as to what files were current.

I also removed from the repository. The database file is created when the app is run. Having this within the repository increases the risk of test user details being exposed and decreases portability of the project. The database models, sample product creation and the code however remains within the project so the database can still be recreated.

I also updated the README to remove any redundant download links to clarify the current state of the project within the README rather than a previous state.

## 9 October 2026 - final structure, documentation, and assessment evidence
I removed an old Linearfy folder and uploaded the final project structure. This simplified navigation of the project and ensured that the current project images, static files, templates, and app files are all present in one location.

I also replaced the previous README with a more detailed one which includes information about the project, target users, the technology used, the database used, security, testing, relevant implications and iterative development. This is to demonstrate the iterative development process of Linearfy which involved planning, testing, feedback and iteration.

## How testing influenced the development
The most significant change was in respect to stock control. Initially it seemed that restricting the quantity controls in the frontend of the app were sufficient. Additional testing however revealed that stock could alter after an item has been added to the cart. In response to this a second stock check is now carried out when the order is placed through the Flask backend. This prevents negative stock levels being created and ensures that an order will not be completed if a requested quantity is no longer available. 

There was also enforcement of no duplicated items on the wish list using a constraint in the database, checking admin only features, implementation of a system for seller listings and moderation, input sanitisation, and better visualisation of the current status of items via stock and notifications. All of these enhancements demonstrate that the final system has been enhanced as a result of testing, and not implemented in one hit.

