from dash import html, dcc
import dash_bootstrap_components as dbc

def create_landing_page():
    return html.Div(id='landing-page', className='background', children=[
        dbc.Container([
            dbc.Card(className='card', style={'border': 'none'}, children=[
                html.H1("PDF Knowledge Base & Chatbot", className='heading'),
                html.P("Upload PDFs to build your knowledge base or chat with our AI assistant.",
                      style={'fontSize': '1.2rem', 'marginBottom': '2rem', 'color': '#666'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Upload PDF", id="go-upload", className="button",
                                 color="primary", size="lg")
                    ], width=12, className="mb-3"),
                    dbc.Col([
                        dbc.Button("Chat Now", id="go-chatbot", className="button",
                                 color="secondary", size="lg")
                    ], width=12)
                ])
            ])
        ])
    ])

def create_upload_page():
    return html.Div(id='upload-page', style={'display': 'none'}, className='background', children=[
        dbc.Container([
            dbc.Card(className='card', style={'border': 'none'}, children=[
                html.H1("Upload PDFs", className='heading'),
                dcc.Upload(
                    id='upload-pdf',
                    children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt", 
                              style={'fontSize': '3rem', 'marginBottom': '1rem'}),
                        html.P("Drag and Drop or Click to Upload Multiple PDFs")
                    ], style={'textAlign': 'center', 'padding': '2rem', 
                             'border': '2px dashed #ccc', 'borderRadius': '8px'}),
                    style={'cursor': 'pointer'},
                    multiple=True
                ),
                html.Div(id='upload-results'),
                dbc.Progress(id="overall-progress", 
                           style={'marginTop': '1rem', 'height': '0.5rem'}),
                dbc.Button("Back", id="back-to-landing", 
                          className="button", color="secondary")
            ])
        ])
    ])

def create_chat_page():
    return html.Div(id='chat-page', style={'display': 'none'}, className='background', children=[
        dbc.Container([
            dbc.Card(className='card', style={'border': 'none'}, children=[
                html.H1("Chat with AI Assistant", className='heading'),
                html.Div(id='chat-history', style={
                    'height': '400px',
                    'overflowY': 'auto',
                    'padding': '1rem',
                    'border': '1px solid #e0e0e0',
                    'borderRadius': '8px',
                    'marginBottom': '1rem'
                }),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(
                            id='chat-input',
                            placeholder='Type your message...',
                            className='input'
                        ),
                    ], width=9),
                    dbc.Col([
                        dbc.Button("Send", id="chat-send", 
                                 className="button", color="primary")
                    ], width=3)
                ]),
                dbc.Button("Back", id="back-to-landing-chat", 
                          className="button mt-4", color="secondary")
            ])
        ])
    ])