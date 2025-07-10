from flask import Blueprint,render_template, request, redirect
import src.utils.spis as spi_utils
import src.utils.db as db_utils
import src.utils.table as table_utils
from datetime import datetime
import pandas as pd
### DATA ANALYSIS
import plotly.graph_objects as go


module3_bp = Blueprint('module3', __name__)
#!!! IDS USED FOR IDENTIFICATION WITHIN THE TABLE NOT TO IDENTIFY SPI CLASS !!!
graph_map ={ 
    "tozeroy": "≥"
}

spis = [
    { "id": 1, "spi_name": "Nr. of Safety Review Board perfomed", "target_value": 2, "mode": "sum", "sign": "tozeroy" },]
"""
    { "id": 2, "spi_name": "% of Recommendations implemented (YTD)", "target_value": "≥95", "mode": "avg"},
    { "id": 3, "spi_name": "Nr. of Emergency Response (ERP) drill performed", "target_value": "≥1", "mode": "sum"},
    { "id": 4, "spi_name": "Nr. of review of Safety Policy & Objectives", "target_value": "≥ 1", "mode": "sum"},
    { "id": 5, "spi_name": "Nr of Accident", "target_value": "≥ 1", "mode": "sum"},
    { "id": 6, "spi_name": "Nr of Serious Incident", "target_value": "<1", "mode": "avg"},
    { "id": 7, "spi_name": "Nr of Operational Incidents (MOR)", "target_value": "<1", "mode": "avg"},
    { "id": 8, "spi_name": "Nr of Technical Incidents (MOR)", "target_value": "<1 ", "mode": "avg" },
    { "id": 9, "spi_name": "Nr of Safety Reports (Voluntary & confidential) per month", "target_value": "≤2 per 1000FHs", "mode": "avg"},
    { "id": 10, "spi_name": "Nr of Risk Assessments perfomed per month", "target_value": "≤1 per 1000FHs", "mode": "avg"},
    { "id": 11, "spi_name": "Nr of Hazards identified per month", "target_value": "≤1 per 1000FHs", "mode": "avg"},
    { "id": 12, "spi_name": "Nr of new Mitigations validated and implemented per month" },
    { "id": 13, "spi_name": "Nr. of Safety Bulletin published" },
    { "id": 14, "spi_name": "Nr. of Safety Flash published" },
    { "id": 15, "spi_name": "Nr. of Runway Incursions per month (Source: Safety report)" },
    { "id": 16, "spi_name": "Nr. of Wildlife Strike per month (Source: Safety report)" },
    { "id": 17, "spi_name": "Nr. of Level Bust per month (Source: Safety report)" },
    { "id": 18, "spi_name": "Nr. of High speed rejected take-off per month (Source: FDM)" },
    { "id": 19, "spi_name": "Nr. of Take-off with abnormal configuration per month (Source: Safety report)" },
    { "id": 20, "spi_name": "Nr of Insufficient take-off performance per month (Source: FDM)" },
    { "id": 21, "spi_name": "Nr of Unstable Approach per month (Source: FDM)" },
    { "id": 22, "spi_name": "Nr of Abnormal pitch at touchdown per month (Source: FDM)" },
    { "id": 23, "spi_name": "Nr. of Hard landing per month (Source: FDM)" },
    { "id": 24, "spi_name": "Nr of Aircraft lateral deviations at high speed on the ground (beginning of landing roll) per month (Source: FDM, LF010 heading change after nose down)" },
    { "id": 25, "spi_name": "Nr of Aircraft lateral deviations at high speed on the ground (till end of take-off roll) per month (Source: FDM, TF300 Takeoff heading range 100knt to rotation)" },
    { "id": 26, "spi_name": "Nr of Short rolling distance at landing per month (Source: FDM)" },
    { "id": 27, "spi_name": "Nr of (E)GPWS/TAWS Warning Trigger per month (Source: FDM)" },
    { "id": 28, "spi_name": "Nr of Pitch attitude high during take off per month (Source: FDM)" },
    { "id": 29, "spi_name": "Nr of Stall protection trigger per month (Source: FDM)" },
    { "id": 30, "spi_name": "Nr of Excessive speed per month (Source: FDM)" },
    { "id": 31, "spi_name": "Nr of Excessive vertical speed during climb per month (Source: FDM)" },
    { "id": 32, "spi_name": "Nr of Excessive vertical speed during descent per month (Source: FDM)" },
    { "id": 33, "spi_name": "Nr of Low go-around or rejected landing per month (Source: FDM)" },
    { "id": 34, "spi_name": "Nr of Reduced margin to manoeuvrability speed per month (Source: FDM)" },
    { "id": 35, "spi_name": "Nr of TCAS/ACAS Resolution Advisory per month (Source: FDM)" },
    { "id": 36, "spi_name": "Nr. of COM flights captured by FDM per month" },
    { "id": 37, "spi_name": "Nr of of fatigue report form received per month" }
]
"""
graphs_spis = [ ### Note all the SPIs need to be in the spis list to be displayed in the graphs
    {"spi_name": "Nr. of Safety Review Board perfomed" },
    {"spi_name": "% of Recommendations implemented (YTD)" },
]

@module3_bp.route('/module/3', methods=['GET', 'POST'])
def module_3():#!!!!ID USATO PER INDIVISUARE ISTANZA DI SPI NON CLASSE DI SPI!!!!
    """
    Route for the module 3, which handles the safety data.
    """
    # Recupera i dati esistenti dal database
    table=table_utils.get_table()
    user_agent=request.headers.get('User-Agent')

    start_date = request.args.get('start_date', datetime.today().replace(month=1).strftime('%Y-%m'))
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m'))
    
    # Convert to datetime objects
    start_date_dt = datetime.strptime(start_date, '%Y-%m')
    end_date_dt = datetime.strptime(end_date, '%Y-%m')
    if (
        ('Firefox' in user_agent) or
        ('Safari' in user_agent and 'Chrome' not in user_agent and 'Edg/' not in user_agent)
    ):
        start_date_value = start_date_dt.strftime('%Y-%m-%d')
        end_date_value = end_date_dt.strftime('%Y-%m-%d')
        date_type = 'date'
    else:
        start_date_value = start_date_dt.strftime('%Y-%m')
        end_date_value = end_date_dt.strftime('%Y-%m')
        date_type = 'month'

    return render_template('SAFETY.html', table=table, start_date_value=start_date_value, end_date_value=end_date_value, date_type=date_type)

@module3_bp.route('/module/3/graphs')
def module_3_graphs(processed_data):
    """
    args:
        processed_data (list): List of processed SPI + data to generate the graphs with. NB: the spis are already filtered and processed.
    Returns:
        graphs (str): html for the graphs.
    """
    
    graphs = ""
    for processed_spi in processed_data:
        processed_spi = {
            'id': processed_spi['id'],
            'spi_name': processed_spi['spi_name'],
            'data': processed_spi['data'],
            'target_value': processed_spi['target_value'],
            'sign': graph_map.get(processed_spi['sign'], processed_spi['sign'])
        }
        graphs += f'<div class="graph-item">{interactive_plot(pd.DataFrame(processed_spi["data"]["values"]), processed_spi["spi_name"], processed_spi["target_value"], processed_spi["sign"])}</div>'
    
    return graphs

def interactive_plot(df, spi_name, target_value=0, fill='tozeroy'):
    """ 
        Generate an interactive plot for the given DataFrame and SPI name.
    """

    fig = go.Figure()
    
    fig.update_layout(
        title= f'{spi_name} - over time',
        xaxis_title='Entry Date',
        yaxis_title='SPI Value',
        template='plotly_white'
    )

    df['entry_date'] = pd.to_datetime(df['entry_date'])  # Ensure entry_date is in datetime format

    min_date = df['entry_date'].min()
    max_date = df['entry_date'].max()
    # Set interval (e.g., every 1 month)
    fig.update_xaxes(
        range=[min_date, max_date],
        dtick="M1", 
        tickformat="%Y-%m"
    )
    # Graph
    fig.add_trace(
        go.Scatter(
            x=df['entry_date'],
            y=df['value'],
            mode='lines+markers',
            name='SPI Value',
            line=dict(color='blue', width=2),
            marker=dict(size=5)
        )
    )
    # target
    fig.add_trace(
        go.Scatter(
            x=[min_date, max_date],
            y=[target_value, target_value],
            mode='lines',
            name='Target Value',
            line=dict(color='red', dash='dash'),
            showlegend=True,
            fill=fill
        )
    )
    return fig.to_html(full_html=True, include_plotlyjs='cdn')

@module3_bp.route('/module/3/save', methods=['POST'])
def module_3_save():
    """
    Endpoint to save the data from the form.
    """
    conn = db_utils.get_db_connection()

    new_data = []

    # Ottieni i dati dal modulo
    reference_month = datetime.today().month  # Usa il mese corrente come riferimento
    reference_year = datetime.today().year  # Usa l'anno corrente come riferimento
    for spi in spis:
        spi_id = spi['id']
        spi_value = request.form.get(f'{spi_id}')
        if spi_value != '':
                if spi_id == 2:  
                    # For SPI 2, convert the value to a percentage
                    spi_value = float(spi_value)
                else:
                    spi_value = int(spi_value)
                
                # Aggiungi i dati al buffer
                new_data.append((spi['spi_name'], spi_value, reference_month, reference_year))
                # perform commit
        else:
            spi_value = None
    # Commit all data in one go
    # Commit the update to the database
    db_utils.commit_update_data(new_data, conn)

    return "OK", 200