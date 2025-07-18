import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def interactive_plot(df, spi_name, target_value=[], fill='tozeroy'):
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
    if isinstance(target_value, list) and len(target_value) > 1:
        colors = get_color_scale(len(target_value))
        for idx, value in enumerate(target_value):
            color = f'rgba({int(colors[idx][0]*255)},{int(colors[idx][1]*255)},{int(colors[idx][2]*255)},1)'
            fig.add_trace(
                go.Scatter(
                    x=[min_date, max_date],
                    y=[value, value],
                    mode='lines',
                    name='Target Value'+ f' {value}',
                    line=dict(color=color, width=2, dash='dash')
                )
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=[min_date, max_date],
                y=[target_value, target_value],
                mode='lines',
                name='Target Value',
                line=dict(color='red', width=2, dash='dash')
            )
        )
    return fig.to_html(full_html=True, include_plotlyjs='cdn')

def get_color_scale(n):
    # Returns n colors from green to red
    cmap = plt.get_cmap('RdYlGn')
    out = []
    for i in range(n):
        out.append(cmap(i/(n-1 if n > 1 else 1)))
    return out[::-1] 

def comparison_plot(spis, graph_name, target_value=[]):
    """
        Generate a comparison plot for the given DataFrame and SPI name.
        args:
            spis: List of SPIs, each containing 'spi_name' and 'data'.
            graph_name: Name of the graph to be displayed.
            target_value: Target value(s) to be displayed as a horizontal line(s).
    """
    fig = go.Figure()
    
    fig.update_layout(
        title= f'{graph_name} - over time',
        xaxis_title='Entry Date',
        yaxis_title='SPI Value',
        template='plotly_white'
    )

    for spi in spis:
        start_index = spi['spi_name'].index('I-MSC')
        end_index = start_index + 6
        spi['spi_name'] = spi['spi_name'][start_index:end_index]  # Extract the relevant part of the SPI name

    df = pd.DataFrame()
    for spi in spis:# Loop through each SPI and concatenate data
        spi_df = pd.DataFrame(spi['data'])
        spi_df['entry_date'] = pd.to_datetime(spi_df['entry_date'])
        spi_df['aircraft'] = spi['spi_name']
        spi_df['value'] = spi_df['value'].astype(float)  # Ensure value is float
        df = pd.concat([df, spi_df], ignore_index=True)
        df.sort_values(by='entry_date', inplace=True)

    # Graphs
    for aircraft, group in df.groupby('aircraft'):
        fig.add_trace(
            go.Scatter(
                x=group['entry_date'],
                y=group['value'],
                mode='lines+markers',
                name=f'{aircraft}',
                line=dict(width=2),
                marker=dict(size=5)
            )
        )
    
    min_date = df['entry_date'].min()
    max_date = df['entry_date'].max()

    if isinstance(target_value, list) and len(target_value) > 1:
        colors = get_color_scale(len(target_value))
        for idx, value in enumerate(target_value):
            color = f'rgba({int(colors[idx][0]*255)},{int(colors[idx][1]*255)},{int(colors[idx][2]*255)},1)'
            fig.add_trace(
                go.Scatter(
                    x=[min_date, max_date],
                    y=[value, value],
                    mode='lines',
                    name='Target Value'+ f' {value}',
                    line=dict(color=color, width=2, dash='dash')
                )
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=[min_date, max_date],
                y=[target_value, target_value],
                mode='lines',
                name='Target Value',
                line=dict(color='red', width=2, dash='dash')
            )
        )
    
    return fig.to_html(full_html=True, include_plotlyjs='cdn')