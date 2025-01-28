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
                        dbc.Button("Upload PDF", id="go-upload", 
                                 className="button w-100",
                                 color="primary", 
                                 size="lg")
                    ], width=6, className="text-center px-2"),
                    dbc.Col([
                        dbc.Button("Chat Now", id="go-chatbot", 
                                 className="button w-100",
                                 color="secondary", 
                                 size="lg")
                    ], width=6, className="text-center px-2")
                ], className="g-0 justify-content-center")
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
                    ], style={
                        'textAlign': 'center',
                        'padding': '1rem',
                        'border': '1px solid #e0e0e0',
                        'borderRadius': '8px',
                        'height': '400px',
                        'marginBottom': '1rem',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    }),
                    style={'cursor': 'pointer'},
                    multiple=True
                ),
                dbc.Progress(id="overall-progress", 
                        style={'height': '0.5rem', 'marginBottom': '1rem'}),
                html.Div(id='upload-results'),
                dbc.Button("Back", id="back-to-landing", 
                        className="button mt-3", color="secondary")
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
                    ], width=10, className='pe-2'),  # Added padding-end
                    dbc.Col([
                        dbc.Button("Send", id="chat-send", 
                                 className="button w-100", color="primary")
                    ], width=2)
                ], className='g-0'),
                dbc.Button("Back", id="back-to-landing-chat", 
                          className="button mt-4", color="secondary")
            ])
        ])
    ])