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

module1_OCC_ = Blueprint('module1_OCC_', __name__)
# TODO CONSIDERARE SE FARE TABELLE SPECIFICHE PER SEZIONE
spis = {}
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

    all_data = auto_values()

    session['all_data'] = all_data

    table=table_utils.get_table(all_data, graph_map, 'occ_table.html')

    return render_template('OCC.html', table=table, all_data=all_data, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=aircafts)

@module1_OCC_.route('/module/1/graphs')
def module_1_OCC_graphs():
    """Route for generating graphs for the OCC module.
    """

def auto_values():# move this to upload 
    """
    Calculate the SPIs for the OCC module.
    """

    all_data = session.get('all_data', [])
    if not all_data:
        return "No data available for calculations."

    if len(all_data) < 2:
        return "Insufficient data for calculations."

    # Find indices for "Flight cycles" and "Flight time"
    flight_cycles_idx = next((idx for idx, spi in enumerate(all_data) if "Flight cycles" in spi['spi_name']), None)
    flight_time_idx = next((idx for idx, spi in enumerate(all_data) if "Flight time" in spi['spi_name']), None)

    if flight_cycles_idx is None or flight_time_idx is None:
        return "Insufficient data for calculations."

    flight_cycles_data = all_data[flight_cycles_idx]['data']
    flight_time_data = all_data[flight_time_idx]['data']

    fhrc = spi_utils.get_spi_by_name("Flight hours per cycle")

    processed_data = {
        'id': fhrc['id'],
        'spi_name': "Flight hours per cycle",
        'data': [],
        'target_value': fhrc['target_value'],
        'mode': fhrc['mode'],
        'table': fhrc['table'],
        'sign': fhrc['sign']
    }

    # Assume both data lists are aligned by index
    for i in range(min(len(flight_cycles_data), len(flight_time_data))):
        flight_cycles = flight_cycles_data[i]['value']
        flight_time = flight_time_data[i]['value']
        if flight_cycles > 0:
            flight_hours_per_cycle = flight_time / flight_cycles
        else:
            flight_hours_per_cycle = 0
            
        processed_data['data'].append({
            'value': round(flight_hours_per_cycle, 2),
            'entry_date': flight_cycles_data[i]['entry_date']
        })

    all_data.append(processed_data)

    acd_m = spi_utils.get_spi_by_name("Aircraft daily utilization per month")

    processed_data = {
        'id': acd_m['id'],
        'spi_name': "Aircraft daily utilization per month",
        'data': [],
        'target_value': acd_m['target_value'],
        'mode': acd_m['mode'],
        'table': acd_m['table'],
        'sign': acd_m['sign']
    }
    # Calculate daily utilization for each flight time entry based on the previous month days
    for i in range(len(flight_time_data)):
        flight_time = flight_time_data[i]['value']
        if flight_time > 0:
            ac_daily_utilization = flight_time / calendar.monthrange(flight_time_data[i]['entry_date'].year, flight_time_data[i]['entry_date'].month)[1]
        else:
            ac_daily_utilization = 0
        
        processed_data['data'].append({
            'value': round(ac_daily_utilization, 2),
            'entry_date': flight_time_data[i]['entry_date']
        })
#TODO SAVE THIS TO DB
    all_data.append(processed_data)

    return all_data