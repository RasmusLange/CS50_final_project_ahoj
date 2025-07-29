# CS50 Final Project: Ahoj, the simple board / chat platform.
#### Video Demo:  [https://youtu.be/B4f-cCBaPWg]
#### Description:
Ahoj! is my CS50 final project - a web application designed to replicate a physical posting board in a “modernized” digital format. It lets users create, join, and post single messages to boards, with “notifications” for new messages on subscribed boards shown on the index page. The application is built using Flask, SQL for data persistence, HTML and Jinja for templating, Bootstrap, and a tiny bit of CSS for styling.
Below is a technical description of the user journey for Ahoj!:
# Initial access and authentication
When navigating to the application's base URL, the system immediately redirects unauthenticated users to a dedicated login page. Boring from the Week 9 Finance problem, any functionality except /login and /register is hidden behind the login decoration and redirects the user to /login when attempting to access any other pages.
Users are provided with an option to create a new account. This process involves submitting a unique username, password, and confirmation of the password.
A successful registration operation results in the creation of a new user record in the SQL database, by hashing the password before storage with werkzeug.security.
Confirmations are generally built into the platform to notify the user of whenever something goes on under the hood. For instance, "User successfully created") in highlighted with green or an error message in red. As such, “neutral” messages are highlighted with yellow.
When a user input their registered username and password the backend authenticates these credentials against the stored user data, by making a query to the SQL database and comparing the hashed provided password to the hash stored in the database.
Upon successful authentication, a user session is established, and the user is redirected to the main index page.
# Dashboard / index page
Initial view: After logging in, the user is presented with the index page. This page displays a personalized welcome message.
Ahoj! keeps track of when messages are posted and when the user has last visited a board. As such, new messages in boards the user is a member of will be displayed on the index page. If the user is not yet a member of any boards or has no new messages, the interface prompts them to "join a board,".
# Board Management
Joining and creating boards:
Users can initiate the process of joining or creating a board from the prompt on the index page or navbar at the top of the page. On the /join page the user is met with an input field and a button, where they can provide their desired board name.
The system queries the SQL database to check for the existence of a board with the given name. If the board does not exist, it is created as a new entry in the database. The user is then automatically added as a member and admin of the newly created board.
If the board already exists, the user is simply added as a member to the existing board without admin privileges.
The /boards page dynamically updates to reflect the user's current board memberships, displaying a table of boards they are part of.
For each listed board, the user has options: “Leave” removes the user's membership from the board in the database. The board is removed from their list on the index page and relation in the SQL database. “Visit” navigates the user to the specific board's dedicated page.
# Posting messages
The single message constraint is a core design principle of Ahoj! Each board can only display a single message from each user at a time. This means that when a new message is posted to a board, it overwrites any previously existing message by the user for that specific board. Additionally, to support the index page notification of new messages, the unix timestamp is registered when posting, and also when the user visits a board.
# Board admins
The system distinguishes between regular users and administrators for specific boards, simply controlled by true or false (1 or 0) in the SQL.
On boards where the user is an administrator, a "Manage members" option is available. Admins can promote, demote, and kick other members of the board.
While kicking users is an option, it doesn’t matter much since the kicked user can simply rejoin again. When a user is kicked, they are simply removed from the database, their status as “kicked” is not registered.
Promotion, on the other hand, carries more meaning, since it allows the promoted user to kick and promote as well, giving them the same privileges as the creator of the board.
# Account management
Users have the option to change their username and password.
When a username is changed, the change is instantly reflected across the application. This is due to any actions taken on the platform (i.e., loading a page) directly taps into the SQL database every time. No fancy rendering or caching here!

# The underlying SQL database
Three tables in total are in use, the tables are declared as follows:
boards:
CREATE TABLE boards (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, board_name TEXT NOT NULL);

members:
CREATE TABLE members (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id NUMBER NOT NULL, board_id NUMBER NOT NULL, message TEXT, post_time NUMBER, visit_time NUMBER, admin BOOLEAN NOT NULL);

users:
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);
When viewing any given page, it is likely that multiple tables are in use at one time. It has genuinely been fun trying to figure out what the best way to do this was, and I ended up arriving at three tables.
The number three just kind of felt right for the application. Initially, I had planned more, or to have more information in the “users” and “boards” tables. But I soon realized that given the one-message-per-board constraint used as the main design principle of the application, most data fitted better into the members table.
Boards and users are self-explanatory. They simply have an id and a (board/user)name.
Members keep track of when a user last visited a specific board, when they last posted, what their current message (if any) in the current board is, and whether or not they are an admin.
As I believe my queries show, I learned a lot from this project, and felt more and more comfortable with SQL as I progressed through the different functionality of the platform. Same goes for the Jinja templates that felt a little hard to grasp at firm, but I soon realized could be quite powerful as well.

Thank you so much, CS50 - it’s been a great couple of weeks! :)

# CS50_final_project_ahoj
CS50 Final Project: Ahoj, the simple board / chat platform.
