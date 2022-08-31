# pytils
Utils for data python project.

- _pickledays_ - decorator of class. Save the object state to the filesystem after it's initialization for some defined time. Load object after another call.
- _singleton_ - decorator of class. Share object to all calls. There will be only one instance.
- _logger_ - log the info messages to file, stream and discord. 
- _log_ - decorator of function. Log the function call into the logger.
- _configurator_ - additional method for Dynaconf, which create variable in settings file.
- _pandas_table_ - additional method for pandas, which save the DataFrame to specific sheet. Differs from standard df.to_excel by saving other sheets.

# Installation
Directly from github:

    pip install git+https://github.com/Whisperes/pytils.git