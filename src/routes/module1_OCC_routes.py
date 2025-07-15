from flask import Blueprint,render_template, request, session
import src.utils.spis as spi_utils
import src.utils.db as db_utils
import src.utils.table as table_utils
import src.utils.time_utils as time
from src.utils.graphs import interactive_plot
from datetime import datetime
import calendar
### DATA ANALYSIS
import plotly.graph_objects as go
import json
module1_OCC_ = Blueprint('module1_OCC_', __name__)
# TODO CONSIDERARE SE FARE TABELLE SPECIFICHE PER SEZIONE
SPIS = [
    { "id": 38, "spi_name": "Flight time -- block hours (HH:MM) - COM flights only", "target_value": 5000, "mode": "sum", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 39, "spi_name": "Flight cycles -- COM flights only", "target_value": 475, "mode": "sum", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 40, "spi_name": "Flight hours per cycle --", "target_value": 8, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 41, "spi_name": "Regularity --", "target_value": 95, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 42, "spi_name": "Departure Punctuality --","target_value": 75, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 43, "spi_name": "Aircraft daily utilization per month --", "target_value": 475, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"}
]
graph_map ={ 
    "tozeroy": "≥"
}

@module1_OCC_.route('/module/1', methods=['GET', 'POST'])
def module_1_OCC():
    """
    Route for Operational Control Center (OCC) module, which handles the safety data.
    """
    
    cur = db_utils.get_db_connection().cursor()
    user_agent=request.headers.get('User-Agent')
    if (
        ('Firefox' in user_agent) or
        ('Safari' in user_agent and 'Chrome' not in user_agent and 'Edg/' not in user_agent)
    ):
        start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    else:
        start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1))
        end_date = request.args.get('end_date', datetime.today())
    

    all_data = db_utils.get_data_table('occ_flight_data', start_date=start_date, end_date=end_date, cur=cur)
    
    if not all_data:
        return render_template('OCC.html', table=None, all_data=None, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=[])          

    session['all_data'] = all_data

    aircafts = []

    for spi in all_data:
        if spi['spi_name'].__contains__('I-MSC'):
            start_index = spi['spi_name'].index('I-MSC')
            end_index = start_index + 6
            if spi['spi_name'][start_index:end_index] not in aircafts:
                aircafts.append(spi['spi_name'][start_index:end_index])

    #auto_vals = auto_values()

    table=table_utils.get_table(all_data, graph_map, 'occ_table.html')

    return render_template('OCC.html', table=table, all_data=all_data, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=aircafts)

@module1_OCC_.route('/module/1/graphs')
def module_1_OCC_graphs():
    """Route for generating graphs for the OCC module.
    """

def auto_values(flight_cycles_data, flight_time_data):
    """
    Calculate the SPIS for the OCC module.
    """

    all_data = session.get('all_data', [])
    if not all_data:
        return "No data available for calculations."

    if len(all_data) < 2:
        return "Insufficient data for calculations."

    if flight_cycles_data is None or flight_time_data is None:
        return "Insufficient data for calculations."

    fhrc = spi_utils.get_spi_by_name("Flight hours per cycle")

    ac_daily_utilization = {}

    if flight_cycles_data is None or flight_cycles_data['value'] == 0:
        flight_hours_per_cycle = 0
    else:
        flight_hours_per_cycle = flight_time_data['value'] / flight_cycles_data['value']

    flight_hours_per_cycle = {
        'id': fhrc['id'],
        'spi_name': "Flight hours per cycle",
        'data': [{
            'value': round(flight_hours_per_cycle, 2),
            'entry_date': flight_cycles_data['entry_date']}],
        'target_value': fhrc['target_value'],
        'mode': fhrc['mode'],
        'table': fhrc['table'],
        'sign': fhrc['sign']
        }

    acd_m = spi_utils.get_spi_by_name("Aircraft daily utilization per month")

    if flight_time_data is not None and flight_time_data['value'] is not None:
        ac_daily_utilization = flight_time_data / calendar.monthrange(flight_time_data['entry_date'].year, flight_time_data['entry_date'].month)[1]
    else:
        ac_daily_utilization = 0

    ac_daily_utilization = {
        'id': acd_m['id'],
        'spi_name': "Aircraft daily utilization per month",
        'data': [{
            'value': round(ac_daily_utilization, 2),
            'entry_date': flight_time_data['entry_date']}],
        'target_value': acd_m['target_value'],
        'mode': acd_m['mode'],
        'table': acd_m['table'],
        'sign': acd_m['sign']
    }
    # Calculate daily utilization for each flight time entry based on the previous month days
    
    return [flight_hours_per_cycle, ac_daily_utilization]

@module1_OCC_.route('/module/1/save/<spi_name>', methods=['POST'])
def save_data(spi_name=None):#we pass an spi_name if we need to save a single spi
    """
    Save the data to the database.
    """

    conn = db_utils.get_db_connection()

    new_data = []
    reference_month = datetime.today().month  # Usa il mese corrente come riferimento
    reference_year = datetime.today().year  # Usa l'anno corrente come riferimento
    for spi in SPIS:
        spi_id = spi['id']
        spi_value = request.form.get(f'{spi_id}')
        if spi_value != '' and spi_value is not None:
            if spi_id == 41 or spi_id == 42:
                spi_value = float(spi_value)
            if spi_id == 40 or spi_id == 43 or spi_id == 38:  
                spi_value = time.time_to_minutes((spi_value).split(':')[0],(spi_value).split(':')[1])
            else:
                spi_value = int(spi_value)

            # Aggiungi i dati al buffer
            new_data.append((spi_name if spi_name else spi['spi_name'], spi_value, reference_month, reference_year))
            # perform commit
        else:
            spi_value = None


    db_utils.commit_update_data(new_data, conn, 'occ_flight_data')

    return "OK", 200

@module1_OCC_.route('/module/1/submit_spis', methods=['POST'])
def submit_spis():
    """
    Submit the SPIS data to the database.
    """
    data = request.get_json()

    print("Received data:", data)

    new_data = []
    reference_month = datetime.today().month
    reference_year = datetime.today().year

    if not data:
        return "No data provided", 400
    for aircraft_spis in data:
        for spi_name, value in aircraft_spis.items():
            if spi_name == 'aircraft':
                continue
            new_data.append((spi_name, value, reference_month, reference_year))

        # Save the data for each SPI
    
    db_utils.commit_update_data(new_data, db_utils.get_db_connection(), 'occ_flight_data')

    return "Data submitted successfully", 200

@module1_OCC_.route('/module/1/ac_data', methods=['GET'])
def get_ac_data():
    """
    Get the data for a specific aircraft.
    """
    aircraft = request.args.get('aircraft', None)

    ac_data = []

    cur = db_utils.get_db_connection().cursor()

    if aircraft.__contains__('I-MSC'):
        for spi in SPIS:
            spi_copy = spi.copy()
            ac_index = spi_copy['spi_name'].index('--') + 1
            spi_copy['spi_name'] = spi_copy['spi_name'][:ac_index] +"("+ aircraft +")"+ spi_copy['spi_name'][ac_index:]
            data = db_utils.get_data_spi(spi_copy['spi_name'], datetime.today().replace(month=1, day=1), datetime.today(), cur, spi['table'])
            if data:
                ac_data.append({
                    'id': spi_copy['id'],
                    'spi_name': spi_copy['spi_name'],
                    'data': data,
                    'target_value': spi_copy['target_value'],
                    'mode': spi_copy['mode'],
                    'table': spi_copy['table'],
                    'sign': spi_copy['sign']
                })

        if not ac_data:
            return "No data found for the specified aircraft."

        return table_utils.get_table(ac_data, graph_map, 'occ_table.html')
    
    else:
        return "Invalid aircraft specified.", 400