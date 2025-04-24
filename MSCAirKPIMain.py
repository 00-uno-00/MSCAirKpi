import psycopg2
from flask import Flask, render_template, request, redirect, g
import webbrowser
from threading import Timer
import os

app = Flask(__name__)

# PostgreSQL database connection configuration
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

# Route for the Intro Page
@app.route('/')
def intro_page():
    return render_template('intro_page.html')

# Route for the Landing Page
@app.route('/landing')
def landing_page():
    return render_template('landing_page.html')

# Route for Module 1 (OCC Department)
@app.route('/module/1', methods=['GET', 'POST'])
def module_1():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        flight_cycle = request.form.get('flight_cycle')
        flight_hours = request.form.get('flight_hours')
        flight_minutes = request.form.get('flight_minutes')
        reference_year = request.form.get('reference_year')
        reference_month_abbr = request.form.get('reference_month')  # Es. "Jan"

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO occ_flight_data (flight_cycle, flight_hours, flight_minutes, reference_month)
                VALUES (%s, %s, %s, %s)
            """, (flight_cycle, flight_hours, flight_minutes, reference_month))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/1')

    # Recupera i dati esistenti dal database
    try:
        cur.execute("""
            SELECT id, flight_cycle, flight_hours, flight_minutes, reference_month
            FROM occ_flight_data
            ORDER BY reference_month ASC
        """)
        flight_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        flight_data = []

    cur.close()

    # Non elaborare reference_month, visualizzalo direttamente come YYYY-MM
    return render_template('module_1.html', flight_data=flight_data)

@app.route('/module/1/edit/<int:id>', methods=['GET', 'POST'])
def edit_flight_data(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i nuovi dati dal modulo
        flight_cycle = int(request.form.get('flight_cycle'))
        flight_hours = int(request.form.get('flight_hours'))
        flight_minutes = int(request.form.get('flight_minutes'))
        reference_month = request.form.get('reference_month')

        # Aggiorna i dati nel database
        try:
            cur.execute("""
                UPDATE occ_flight_data
                SET flight_cycle = %s, flight_hours = %s, flight_minutes = %s, reference_month = %s
                WHERE id = %s
            """, (flight_cycle, flight_hours, flight_minutes, reference_month, id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error updating data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/1')

    # Recupera i dati esistenti per precompilare il modulo
    cur.execute("SELECT flight_cycle, flight_hours, flight_minutes, reference_month FROM occ_flight_data WHERE id = %s", (id,))
    flight_data = cur.fetchone()
    cur.close()

    return render_template('edit_flight_data.html', flight_data=flight_data, id=id)

# Route for Module 2 (Safety Control Department)
@app.route('/module/2', methods=['GET', 'POST'])
def module_2():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month_abbr = request.form.get('reference_month')
        reference_year = request.form.get('reference_year')
        percentage = float(request.form.get('percentage'))

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO compliance_data (spi, reference_month, percentage)
                VALUES (%s, %s, %s)
            """, (spi, reference_month, percentage))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/2')

    # Recupera i dati esistenti dal database
    try:
        cur.execute("""
            SELECT id, spi, reference_month, percentage
            FROM compliance_data
            ORDER BY reference_month DESC
        """)
        compliance_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        compliance_data = []

    cur.close()
    return render_template('module_2.html', compliance_data=compliance_data)

# Route for Module 3 (Pilot Training Department)
@app.route('/module/3', methods=['GET', 'POST'])
def module_3():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month = request.form.get('reference_month')  # Ora contiene solo il mese (es. "Jan")
        reference_year = request.form.get('reference_year')

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO safety_data (spi, reference_month, reference_year)
                VALUES (%s, %s, %s)
            """, (spi, reference_month, reference_year))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/3')

    # Recupera i dati esistenti dal database
    try:
        cur.execute("""
            SELECT id, spi, reference_month, reference_year, created_at
            FROM safety_data
            ORDER BY created_at DESC
        """)
        safety_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        safety_data = []

    cur.close()
    return render_template('module_3.html', safety_data=safety_data)

# Route for Module 4 (CAMO Department)
@app.route('/module/4', methods=['GET', 'POST'])
def module_4():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month_abbr = request.form.get('reference_month')
        reference_year = request.form.get('reference_year')
        value = int(request.form.get('value'))

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO camo_data (spi, reference_month, reference_year, value)
                VALUES (%s, %s, %s, %s)
            """, (spi, reference_month, reference_year, value))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/4')

    # Recupera i dati esistenti dal database
    try:
        cur.execute("""
            SELECT id, spi, reference_month, reference_year, value, created_at
            FROM camo_data
            ORDER BY created_at DESC
        """)
        camo_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        camo_data = []

    cur.close()
    return render_template('module_4.html', camo_data=camo_data)

# Route for Module 5 (Ground Operations Department)
@app.route('/module/5', methods=['GET', 'POST'])
def module_5():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month_abbr = request.form.get('reference_month')  # Es. "Jan"
        reference_year = request.form.get('reference_year')  # Es. "2032"
        value = int(request.form.get('value'))  # Accetta solo interi

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO ground_ops_data (spi, reference_month, value)
                VALUES (%s, %s, %s)
            """, (spi, reference_month, value))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/5')

    # Recupera i dati esistenti
    try:
        cur.execute("""
            SELECT id, spi, reference_month, value
            FROM ground_ops_data
            ORDER BY reference_month DESC
        """)
        ground_ops_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        ground_ops_data = []

    cur.close()
    return render_template('module_5.html', ground_ops_data=ground_ops_data)

# Route for Module 6 (Crew Department)
@app.route('/module/6', methods=['GET', 'POST'])
def module_6():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month_abbr = request.form.get('reference_month')  # Es. "Jan"
        reference_year = request.form.get('reference_year')  # Es. "2032"
        value = float(request.form.get('value'))  # Accetta valori in percentuale

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO crewtng_data (spi, reference_month, value)
                VALUES (%s, %s, %s)
            """, (spi, reference_month, value))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/6')

    # Recupera i dati esistenti
    try:
        cur.execute("""
            SELECT id, spi, reference_month, value
            FROM crewtng_data
            ORDER BY reference_month DESC
        """)
        crewtng_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        crewtng_data = []

    cur.close()
    return render_template('module_6.html', crewtng_data=crewtng_data)

# Route for Module 7 (Flight Ops Department)
@app.route('/module/7', methods=['GET', 'POST'])
def module_7():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month_abbr = request.form.get('reference_month')  # Es. "Jan"
        reference_year = request.form.get('reference_year')  # Es. "2032"
        value = int(request.form.get('value'))  # Accetta solo interi

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO flight_ops_data (spi, reference_month, value)
                VALUES (%s, %s, %s)
            """, (spi, reference_month, value))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/7')

    # Recupera i dati esistenti
    try:
        cur.execute("""
            SELECT id, spi, reference_month, value
            FROM flight_ops_data
            ORDER BY reference_month DESC
        """)
        flight_ops_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        flight_ops_data = []

    cur.close()
    return render_template('module_7.html', flight_ops_data=flight_ops_data)

# Route for Module 8 (Cargo Department)
@app.route('/module/8', methods=['GET', 'POST'])
def module_8():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('spi')
        reference_month_abbr = request.form.get('reference_month')  # Es. "Jan"
        reference_year = request.form.get('reference_year')  # Es. "2032"
        value = int(request.form.get('value'))  # Accetta valori long

        # Mappa dei mesi abbreviati a numeri
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }

        # Combina anno e mese in formato YYYY-MM
        reference_month = f"{reference_year}-{month_map[reference_month_abbr]}"

        # Inserisci i dati nel database
        try:
            cur.execute("""
                INSERT INTO cargo_data (spi, reference_month, value)
                VALUES (%s, %s, %s)
            """, (spi, reference_month, value))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/8')

    # Recupera i dati esistenti
    try:
        cur.execute("""
            SELECT id, spi, reference_month, value
            FROM cargo_data
            ORDER BY reference_month DESC
        """)
        cargo_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        cargo_data = []

    cur.close()
    return render_template('module_8.html', cargo_data=cargo_data)

# Route for Reporting
@app.route('/reporting', methods=['GET'])
def reporting():
    # Aggiungi qui la logica per generare e visualizzare i report
    return render_template('reporting.html')

# Success Page
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    # Funzione per aprire il browser predefinito (opzionale per Render)
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    # Ottieni la porta dalla variabile di ambiente (default: 5000)
    port = int(os.environ.get("PORT", 5000))

    # Avvia il server Flask
    app.run(host="0.0.0.0", port=port, debug=False)