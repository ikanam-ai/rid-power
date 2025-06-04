import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime


# Настройка цветовой палитры
BACKGROUND_COLOR = '#000000'
TEXT_COLOR = '#FFFFFF'
ACCENT_COLOR = '#00CC96'
FONT_FAMILY_HEADER = 'Unbounded, sans-serif'
FONT_FAMILY_BODY = 'Inter, sans-serif'

# Подготовка данных
# 1. Распределение по разделам MPK
section_counts = pd.read_csv('section_counts.csv')

# 2. Топ-10 подклассов IPC
ipc_counts = pd.read_csv('ipc_counts.csv')

# 3. Динамика по годам
yearly_counts = pd.read_csv('yearly_counts.csv')

# 4. Сезонность по месяцам
monthly_counts = pd.read_csv('monthly_counts.csv')


# Создаем приложение Dash
app = dash.Dash(__name__)

# Глобальные стили через CSS (без изменений)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Анализ патентной активности</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Unbounded:wght@900&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                background-color: #000000;
                color: #FFFFFF;
                font-family: Inter, sans-serif;
            }
            .chart-container {
                background-color: #000000;
                padding: 20px;
                margin: 10px auto;
                border-radius: 8px;
                max-width: 1500px;
            }
            .header {
                text-align: center;
                padding: 30px 20px;
                background-color: #000000;
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

app.layout = html.Div([
    html.Div([
        html.H1("Анализ патентной активности", style={
            'fontFamily': FONT_FAMILY_HEADER,
            'fontWeight': 900,
            'color': TEXT_COLOR,
            'fontSize': '2.5rem'
        }),
        html.P("Визуализация ключевых показателей патентной активности", style={
            'fontFamily': FONT_FAMILY_BODY,
            'color': '#AAAAAA',
            'marginTop': '10px'
        })
    ], className='header'),
    
    # График 1: Распределение по разделам MPK (ИСПРАВЛЕНО)
    html.Div([
        dcc.Graph(
            id='mpk-pie',
            figure={
                'data': [go.Pie(
                    labels=section_counts.mpk_section_name,
                    values=section_counts['count'],
                    hole=0.3,
                    textinfo='percent+label',
                    marker=dict(colors=px.colors.qualitative.Pastel)  # Закрыта скобка
                )],  # Закрыта скобка
                'layout': go.Layout(
                    title={
                        'text': "Распределение патентов по разделам MPK",
                        'font': {
                            'family': FONT_FAMILY_HEADER,
                            'size': 24,
                            'color': TEXT_COLOR
                        },
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    height=600,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY),
                    showlegend=False,
                    hoverlabel=dict(
                        font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY)
                    )
                )
            }
        )
    ], className='chart-container'),
    
    # График 2: Топ-10 подклассов IPC
    html.Div([
        dcc.Graph(
            id='ipc-bars',
            figure={
                'data': [go.Bar(
                    x=ipc_counts['count'],
                    y=ipc_counts.IPC_Subclass_Name,
                    orientation='h',
                    marker_color=px.colors.qualitative.Pastel,
                    text=ipc_counts.IPC_Subclass_Name,
                    textposition='auto',
                    textfont=dict(color='black')
                )],
                'layout': go.Layout(
                    title={
                        'text': "Топ-10 подклассов IPC",
                        'font': {
                            'family': FONT_FAMILY_HEADER,
                            'size': 24,
                            'color': TEXT_COLOR
                        },
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    xaxis_title="Количество патентов",
                    height=500,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY),
                    hoverlabel=dict(
                        font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY)
                    ),
                    margin=dict(l=150)
                )
            }
        )
    ], className='chart-container'),
    
    # График 3: Динамика по годам
    html.Div([
        dcc.Graph(
            id='yearly-trend',
            figure={
                'data': [go.Scatter(
                    x=yearly_counts['year'],
                    y=yearly_counts['counts'],
                    mode='lines+markers',
                    line=dict(width=3, color=ACCENT_COLOR),
                    marker=dict(size=10, color=ACCENT_COLOR)
                )],
                'layout': go.Layout(
                    title={
                        'text': "Динамика регистрации патентов по годам",
                        'font': {
                            'family': FONT_FAMILY_HEADER,
                            'size': 24,
                            'color': TEXT_COLOR
                        },
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    xaxis_title="Год",
                    yaxis_title="Количество патентов",
                    height=500,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY),
                    hoverlabel=dict(
                        font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY)
                    ),
                    xaxis=dict(showgrid=True, gridcolor='#333'),
                    yaxis=dict(showgrid=True, gridcolor='#333')
                )
            }
        )
    ], className='chart-container'),
    
    # График 4: Сезонность по месяцам
    html.Div([
        dcc.Graph(
            id='monthly-season',
            figure={
                'data': [go.Bar(
                    x=monthly_counts['month_name'],
                    y=monthly_counts['counts'],
                    marker_color=px.colors.sequential.Viridis
                )],
                'layout': go.Layout(
                    title={
                        'text': "Сезонность регистрации патентов",
                        'font': {
                            'family': FONT_FAMILY_HEADER,
                            'size': 24,
                            'color': TEXT_COLOR
                        },
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    xaxis_title="Месяц",
                    yaxis_title="Количество патентов",
                    height=500,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY),
                    hoverlabel=dict(
                        font=dict(color=TEXT_COLOR, family=FONT_FAMILY_BODY)
                    ),
                    xaxis=dict(showgrid=True, gridcolor='#333'),
                    yaxis=dict(showgrid=True, gridcolor='#333')
                )
            }
        )
    ], className='chart-container'),
   
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
