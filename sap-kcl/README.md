# sap-kcl
Code for auto populating KCL SAP template

## Set up
1. Ensure you are running in a virtual environment (eg. see https://www.w3schools.com/python/python_virtualenv.asp)
2. Install needed packages. This can be done using the `requirements.txt` file with the call `pip install -r requirements.txt`.
3. Create a `.env` file in the project root. This is where you save your API keys. These could include `OPENAI_API_KEY`, `GOOGLE_API_KEY`, and `ANTHROPIC_API_KEY`.

## Writing a SAP
This is done using the 'generate_kcl_sap.py' script in the main project folder.
To write a SAP pass the correct protocol path, location for saving the SAP, and SAP name to the `write_sap` function and run the file. This function will create a SAP in a docx and a text file with the raw tags and content for the SAP.
