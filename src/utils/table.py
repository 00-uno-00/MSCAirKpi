from flask import Blueprint,render_template
import src.utils.spis as spi_utils
from datetime import datetime
### DATA ANALYSIS
import plotly.graph_objects as go


def get_table(all_data, graph_map, table):#this should not be exposed 
    """
    Endpoint to retrieve the table data for the selected module.
    Args:
        all_data (list): List of dictionaries containing SPI data. CHECK all_data structure.
        graph_map (dict): Mapping of SPI signs to their graphical representations.
        table (str): The name of the template to render the table.

    Returns:
        html for the table with the data for the selected module.
    """

    processed_data = []# buffer for processed data to be used in the template & graphs

    for spi in all_data:
        spi_values = spi['data']
        processed_spi = {
            'id': spi['id'],
            'spi_name': spi['spi_name'],
            'data': spi_utils.process_data(spi_values, spi['id'], spi['spi_name']),
            'target_value': spi['target_value'],
            'sign': graph_map.get(spi['sign'], spi['sign'])  
        }
        processed_data.append(processed_spi)

    return render_template(table, rows=processed_data, this_month=datetime.today().replace(month=datetime.today().month-1).strftime('%Y-%m'))