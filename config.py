import os 

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root

upload_import_directory = f'{ROOT_DIR}/importhub_uploads/'

if not os.path.exists(upload_import_directory):
    os.mkdir(upload_import_directory)