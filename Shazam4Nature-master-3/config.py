# Written by Gerd Mund & Robert Logiewa

import urllib

# Database connection string
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};Server=tcp:s4n.database.windows.net;Database=s4n-data;Uid=admin-s4n@s4n;Pwd=s4fkie!6302#;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

class Config(object):
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % params
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXECUTOR_PROPAGATE_EXCEPTIONS = True
