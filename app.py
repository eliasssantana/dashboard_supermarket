from dash import Dash, dcc, html, Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

load_figure_template("minty")

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server

app.title = "Dash Supermarket"

df_data = pd.read_csv('./data/supermarket_sales.csv')
df_data['Date'] = pd.to_datetime(df_data['Date'])

# ========== Layout ==========

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            html.H1("Supermarket Sales Analysis", className="text-center")
        ], className="mb-3 mt-3 vw-100"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Filtros", className='text-center'),
                        html.Br(),
                        html.Label("Cidades", id='label-checklist', htmlFor='checklist-cities'),
                        dcc.Checklist(
                            id='checklist-cities',
                            options=[{'label': cidade, 'value': cidade} for cidade in df_data['City'].unique()],
                            value=df_data['City'].unique(),
                            inputStyle={"margin-right": "5px"}
                        ),
                        html.Br(),
                        html.Label("Variável de análise", id='label-radio', htmlFor='radio-variable'),
                        dcc.RadioItems(
                            id='radio-variable',
                            options=["Gross income", "Rating"],
                            value='Gross income',
                            inputStyle={"margin-right": "5px"}
                        )
                    ], className='p-3')
                ]),
            ], sm=2, md=2, lg=2, className="h-100"),
            dbc.Col([
                dbc.Row([
                    dbc.Col([dcc.Graph(id='city_fig')], sm=4, className="h-100"),
                    dbc.Col([dcc.Graph(id='gender_fig')], sm=4, className="h-100"),
                    dbc.Col([dcc.Graph(id='payment_fig')], sm=4, className="h-100")
                ], className="h-100"),
                dbc.Row([
                    dcc.Graph(id='income_per_date_fig', style={"height": "40vh"})
                ], className="h-100"),
                dbc.Row([
                    dcc.Graph(id='income_per_product_fig', style={"height": "40vh"})
                ], className="h-100")
            ], sm=10, md=10, lg=10, className="d-flex flex-column justify-content-between"),
        ], className="vw-100 h-100"),
    ], className="vh-100 vw-100 h-100"),
])

# ========== Callbacks ==========
@app.callback(
        [
            Output('payment_fig', 'figure'),
            Output('income_per_product_fig', 'figure'),
            Output('city_fig', 'figure'),
            Output('income_per_date_fig', 'figure'),
            Output('gender_fig', 'figure'),
        ],
        [
            Input('checklist-cities', 'value'),
            Input('radio-variable', 'value')
        ]
        )
def update_figs(cities, variable):

    var = variable.lower() if variable == 'Gross income' else variable

    operation = np.sum if variable == 'Gross income' else np.mean

    df_filtered = df_data[df_data['City'].isin(cities)]

    df_city = df_filtered.groupby("City")[var].apply(operation).to_frame().reset_index()

    df_gender = df_filtered.groupby(["Gender", "City"])[var].apply(operation).to_frame().reset_index()

    df_payment = df_filtered.groupby("Payment")[var].apply(operation).to_frame().reset_index()

    df_income_time = df_filtered.groupby("Date")[var].apply(operation).to_frame().reset_index().sort_values(by=var, ascending=False)

    df_product_income = df_filtered.groupby(["Product line", "City"])[var].apply(operation).to_frame().reset_index().sort_values(by=var, ascending=False)

    fig_city = px.bar(df_city, x='City', y=var, color='City', title=f'{variable}\nby City', text_auto=True)

    fig_payment = px.bar(df_payment, y='Payment', x=var, color='Payment', title=f'{variable} by Payment Type', orientation='h', text_auto=True)

    fig_gender = px.bar(df_gender, x='Gender', y=var, color='City', title=f'{variable} by Gender', barmode='group', text_auto=True)

    fig_product_income = px.bar(df_product_income, x=var, y='Product line', color='City', title=f'{variable} by Product line', orientation='h', text=[f'R$ {var:.2f}' for var in df_product_income[var]], barmode='relative')

    fig_income_date = px.bar(df_income_time, y=var, x='Date', barmode='relative', title=f'{variable} by Date')

    fig_city.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        yaxis_showgrid=False,
        yaxis_showticklabels=False
    )  

    # Arredonda as bordas das barras - não funciona no horizontal
    # fig_city.update_traces(
    #     marker_cornerradius=5
    # )

    fig_payment.update_layout(
        xaxis_title=None,
        yaxis_title=dict(
            text=None
        ),
        xaxis_showgrid=False,
        xaxis_showticklabels=False,
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis={
            'categoryorder': 'total ascending',
        }
    )     

    fig_payment.update_yaxes(
        ticks='outside'
    )

    fig_gender.update_layout(
        yaxis_title=None,
        yaxis_showticklabels=False,
        yaxis_showgrid=False
    )

    fig_income_date.update_layout(
        yaxis_title=None,
        yaxis_showticklabels=False,
        yaxis_showgrid=False
    )

    fig_product_income.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_showticklabels=False,
        yaxis={
            'categoryorder': 'total ascending',
        },
        margin=dict(t=40, b=20, l=0, r=0)
    )

    # TO DO
    # [x] Adicionar as margens e tamanhos iguais via um for loop
    # [x] O income_per_product_fig tem altura de 500

    return fig_payment, fig_product_income, fig_city, fig_income_date, fig_gender


    # if not cities:
    #     cities = df_data['City'].unique()

    # # Filter the data based on selected cities
    # df_filtered = df_data[df_data['City'].isin(cities)]

    # # Create the figures
    # fig_city = px.histogram(df_filtered, x='City', y=vars, color='City', barmode='group')
    # fig_payment = px.histogram(df_filtered, x='Payment', y=variables, color='Payment', barmode='group')
    # fig_incomer_per_product = px.histogram(df_filtered, x='Product line', y=variables, color='Product line', barmode='group')

    # return fig_city, fig_payment, fig_incomer_per_product



# ========== Run the app ==========

if __name__ == '__main__':
    app.run(debug=False)