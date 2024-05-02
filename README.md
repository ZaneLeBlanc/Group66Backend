# UTD Spring 2024 CS 4485 Group66 Intrusion Detection System (IDS) Using Machine Learning
## Project Description

As the Internet becomes more common in daily life, the rise in cyber threats underscores the urgent need for robust defense mechanisms. An Intrusion Detection System (IDS) stands as a pivotal defense tool against cyber attacks. This project aims to augment the provided
open-source IDS-ML framework through the development of a user-friendly web-based interface and backend database integration, to allow users to gather analytics on intrusion detection data and evaluate algorithm performance.

## How to Run the Project
Make sure to be in the GROUP66BACKEND directory for everything to run correctly

Database setup (SQLite Db):
This will create a database file called test_DB.db under the GROUP66BACKEND directory, which can then be opened using DB Browser (SQLite)

    python Backend/local_db_setup.py

Run models and connect to front end:

    python Backend/interface.py


## How to Use the Project

#### data_models.py

- contains the database and table definitions for our models and a RunHistory table that keeps track of a unique run id for history retrieval
- each model table holds run parameters (for each algorithm in the model) entered by the users, and also holds output parameters for the model that is then given to the front end to display

#### db_session.py

- sets up the connection to the SQLite database for the backend (engine and session)

#### local_db_setup.py

- creates a trigger to create a unique run id for any data row that is inserted into any of the model tables
- creates the database by referencing the engine previously established in db_session.py

#### interface.py

- provides communication with the front end for our three models (LCCDE, MTH, and TreeBased)
- There are PUT and GET endpoints for each of the models

#### helper files (lccde_helper.py, mth_helper.py, treebased_helper.py)

- contains helper methods that facilitate communication between the models, the database, and the front end
- run methods prepopulate json data for empty parameter requests in the front end, models are run using default parameters for each algorithm. Returns model output in json format for front end to display to users
- get_runs methods retrieve all runs from database model table and convert to json for the front end to process and display, used in run history display
- record methods take output from model run (when run method is called) and stores run parameters and outputs into corresponding model table
- MTH and LCCDE helper files use a cursor to execute queries and communicate with the database, TreeBased helper file uses the session (from db_session) to execute queries and communicate with database

#### model files (lccde.py, mth.py, treebased.py)
- these files are modified versions from the original models (https://github.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning)
- algorithms in these models have been modified to run with user specified parameters from our front end


#### misc.
- FCBF_module is needed to run MTH algorithm, also part of Western-OC2-Lab Intrusion detection repository



## Credits

This was a collaborative effort between 5 people for our senior design class at UTD. We were dubbed "Group 66" for the Spring semester of 2024. The following people were involved:

- Zane LeBlanc
- Amy Mendiola
- Aaron Subichev
- Micaela Landauro
- Imad Siddiqui
- Nhut Nguyen
- Rini Patel


MIT License

Copyright (c) 2024 UTDGROUP66-S24

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.