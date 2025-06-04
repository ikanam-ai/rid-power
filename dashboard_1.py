import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Загрузка данных
topic_agg = pd.read_csv('патентная активность по темам.csv', index_col='registration date', parse_dates=True)
topic_agg_quartal = topic_agg.resample('Q').sum()
cumulative_topics = topic_agg.cumsum()

# Опции для выпадающего списка
quartal_options = [
    {'label': f"{ts.to_period('Q')}", 'value': str(ts)}
    for ts in topic_agg_quartal.index
]

# Настройка цветовой палитры
COLOR_PALETTE = px.colors.qualitative.Pastel
BACKGROUND_COLOR = '#000000'
TEXT_COLOR = '#FFFFFF'
LINE_COLOR = '#FFFFFF'
ACCENT_COLOR = '#00CC96'  # Акцентный цвет для выделения элементов

app = dash.Dash(__name__)

# Кастомизация HTML шаблона для глобальных стилей
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Unbounded:wght@900&display=swap" rel="stylesheet">
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                background-color: #000000;
                font-family: Inter, sans-serif;
                color: #FFFFFF;
            }
            .dash-dropdown {
                color: #FFFFFF !important;
            }
            .VirtualizedSelectOption {
                color: #FFFFFF !important;
                background-color: #111111 !important;
            }
            .VirtualizedSelectFocusedOption {
                background-color: #333333 !important;
            }
            .Select-value-label {
                color: #FFFFFF !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div(style={
    'backgroundColor': BACKGROUND_COLOR,
    'color': TEXT_COLOR,
    'fontFamily': 'Inter, sans-serif',
    'minHeight': '100vh',
    'padding': '10px',
    'boxSizing': 'border-box'
}, children=[
    html.H1("Анализ патентов по тематическим кластерам", style={
        'textAlign': 'center',
        'padding': '20px',
        'fontFamily': 'Unbounded, sans-serif',
        'fontWeight': 900,
        'color': TEXT_COLOR,
        'marginBottom': '10px'
    }),
    
    html.Div([
        dcc.Dropdown(
            id='quartal-selector',
            options=quartal_options,
            value=str(topic_agg_quartal.index[-1]),
            clearable=False,
            style={
                'width': '60%',
                'margin': '0 auto',
                'fontFamily': 'Inter',
                'backgroundColor': '#111111',
                'color': TEXT_COLOR,
                'border': '1px solid #333'
            }
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    dcc.Graph(id='treemap-plot', style={'height': '60vh'}),
    dcc.Graph(id='line-plot', style={'height': '50vh'}),
    dcc.Graph(id='cumulative-plot', style={'height': '50vh'})
])

# Кастомизированная функция для treemap
@app.callback(Output('treemap-plot', 'figure'), Input('quartal-selector', 'value'))
def update_treemap(selected_date):
    selected_date = pd.to_datetime(selected_date)
    quartal_data = topic_agg_quartal.loc[selected_date]
    
    df = pd.DataFrame({
        'Тема': quartal_data.index,
        'Количество патентов': quartal_data.values
    })
    
    fig = px.treemap(
        df,
        path=['Тема'],
        values='Количество патентов',
        color='Количество патентов',
        color_continuous_scale='Viridis',
        hover_data=['Количество патентов']
    )
    
    fig.update_traces(
        texttemplate='<b>%{label}</b><br>%{value} патентов',
        textfont=dict(size=16, family='Inter', color=TEXT_COLOR),
        marker_line_width=1,
        marker_line_color=BACKGROUND_COLOR,
        hovertemplate='<b>%{label}</b><br>Количество: %{value}<extra></extra>'
    )
    
    fig.update_layout(
        title={
            'text': f'Распределение патентов ({selected_date.to_period("Q")})',
            'font': {'family': 'Unbounded', 'size': 24, 'color': TEXT_COLOR}
        },
        margin=dict(t=50, l=0, r=0, b=0),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        coloraxis_colorbar_title_font_color=TEXT_COLOR,
        coloraxis_colorbar_tickfont_color=TEXT_COLOR,
        uniformtext=dict(minsize=12, mode='hide')
    )
    
    return fig

# Кастомизированная функция для линейных графиков
@app.callback(
    [Output('line-plot', 'figure'),
     Output('cumulative-plot', 'figure')],
    Input('quartal-selector', 'value')
)
def update_line_plots(selected_date):
    selected_date = pd.to_datetime(selected_date)
    selected_timestamp = selected_date.timestamp() * 1000
    
    # Общие настройки для обоих графиков
    line_style = dict(width=2, dash='solid')
    vline_style = dict(width=2, dash='dash', color=ACCENT_COLOR)
    layout_common = {
        'paper_bgcolor': BACKGROUND_COLOR,
        'plot_bgcolor': BACKGROUND_COLOR,
        'font': {'color': TEXT_COLOR, 'family': 'Inter'},
        'legend': {'font': {'size': 14}, 'title': {'font': {'size': 16}}},
        'hovermode': 'closest',
        'xaxis': {
            'showgrid': True,
            'gridcolor': '#333',
            'gridwidth': 0.5,
            'tickfont': {'size': 12}
        },
        'yaxis': {
            'showgrid': True,
            'gridcolor': '#333',
            'gridwidth': 0.5,
            'tickfont': {'size': 12}
        }
    }
    
    # Первый график - динамика
    line_fig = px.line(
        topic_agg.reset_index(),
        x='registration date',
        y=topic_agg.columns,
        color_discrete_sequence=COLOR_PALETTE
    )
    
    line_fig.update_traces(line=line_style, hovertemplate='<b>%{fullData.name}</b><br>Дата: %{x|%Y-%m-%d}<br>Патентов: %{y}<extra></extra>')
    line_fig.add_vline(x=selected_timestamp, line=vline_style)
    
    line_fig.update_layout(
        title={
            'text': 'Динамика количества патентов по темам',
            'font': {'family': 'Unbounded', 'size': 22, 'color': TEXT_COLOR}
        },
        yaxis_title="Патентов в месяц",
        height=400,
        **layout_common
    )
    
    # Второй график - кумулятивный
    cum_fig = px.line(
        cumulative_topics.reset_index(),
        x='registration date',
        y=cumulative_topics.columns,
        color_discrete_sequence=COLOR_PALETTE
    )
    
    cum_fig.update_traces(line=line_style, hovertemplate='<b>%{fullData.name}</b><br>Дата: %{x|%Y-%m-%d}<br>Накоплено: %{y}<extra></extra>')
    cum_fig.add_vline(x=selected_timestamp, line=vline_style)
    
    cum_fig.update_layout(
        title={
            'text': 'Накопленное количество патентов по темам',
            'font': {'family': 'Unbounded', 'size': 22, 'color': TEXT_COLOR}
        },
        yaxis_title="Общее количество патентов",
        height=400,
        **layout_common
    )
    
    return line_fig, cum_fig

if __name__ == '__main__':
    app.run_server(port=8050)
