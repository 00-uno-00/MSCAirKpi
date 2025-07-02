DATABASE_URL = "postgresql://neondb_owner:npg_ibQE9C0cXNnZ@ep-aged-cake-a2x4wqvv-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

import psycopg2
from flask import g

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return g.db_conn
