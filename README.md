ar trebui sa punem ceva documentatie cand terminam aici

DB.py

Call create_db_and_tables() at application startup to ensure tables are created.
Use get_session() as a dependency in your API endpoints or services to interact with the database.

REQUEST.LOG.py

Represents a log entry for each API request made to the microservice.
Stores details about the operation, its parameters, result, and the time of the request.

Endpoints.py
The endpoints.py file defines and organizes your FastAPI route handlers (API endpoints) using an APIRouter. 
It contains the logic for handling HTTP requests (such as GET, POST, PUT, DELETE) related to your application's resources (e.g., logs). 
This keeps your endpoint logic separate from the main application setup, improving code structure and maintainability.

Test_main.py
The test_main.py file is typically used to write automated tests for your FastAPI application. 
It ensures your endpoints work as expected by simulating HTTP requests and checking responses.