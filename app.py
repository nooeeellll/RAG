import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv

from core.utils import process_uploaded_files, extract_text_from_pdf, split_text
from core.embedding import EmbeddingManager
from core.chatbot import Chatbot
from ui.templates import create_landing_page, create_upload_page, create_chat_page

load_dotenv()

# Initialize components
embedding_manager = EmbeddingManager()
chatbot = Chatbot(embedding_manager)

# Initialize Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'
                ],
                suppress_callback_exceptions=True)

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    create_landing_page(),
    create_upload_page(),
    create_chat_page()
])

@app.callback(
    [Output('upload-results', 'children'),
     Output('overall-progress', 'value')],
    Input('upload-pdf', 'contents'),
    State('upload-pdf', 'filename'),
    prevent_initial_call=True
)
def update_output(contents_list, filenames_list):
    if not contents_list:
        raise PreventUpdate
    
    results, total_chunks = process_uploaded_files(
        contents_list, 
        filenames_list, 
        lambda pdf_file: embedding_manager.process_pdfs_and_upload(
            pdf_file, 
            extract_text_from_pdf, 
            split_text
        )
    )
    
    alerts = []
    for result in results:
        status_color = 'success' if result['status'] == 'success' else 'danger'
        status_icon = '✓' if result['status'] == 'success' else '✗'
        status_text = f"{result['chunks']} chunks processed" if result['status'] == 'success' else result['error']
        
        alerts.append(
            dbc.Alert(
                f"{status_icon} {result['filename']}: {status_text}",
                color=status_color,
                style={'marginBottom': '0.5rem'}
            )
        )
    
    summary = dbc.Alert(
        f"Total: {total_chunks} chunks processed from {len(results)} files",
        color='info',
        style={'marginTop': '1rem'}
    )
    alerts.append(summary)
    
    return alerts, 100

@app.callback(
    [Output('landing-page', 'style'),
     Output('upload-page', 'style'),
     Output('chat-page', 'style')],
    [Input('go-upload', 'n_clicks'),
     Input('go-chatbot', 'n_clicks'),
     Input('back-to-landing', 'n_clicks'),
     Input('back-to-landing-chat', 'n_clicks')]
)
def update_page(upload_clicks, chat_clicks, back_clicks, back_chat_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'go-upload':
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    elif button_id == 'go-chatbot':
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    else:  # back buttons
        return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}

@app.callback(
    [Output('chat-history', 'children'),
     Output('chat-input', 'value')],
    [Input('chat-send', 'n_clicks')],
    [State('chat-input', 'value'),
     State('chat-history', 'children')],
    prevent_initial_call=True
)
def update_chat(n_clicks, message, history):
    if not message:
        raise PreventUpdate
        
    if not history:
        history = []
    elif isinstance(history, str):
        history = [history]
        
    user_message = html.Div(
        f"You: {message}", 
        style={'marginBottom': '0.5rem', 'textAlign': 'right', 'color': '#4a90e2'}
    )
    
    # Get response from chatbot
    bot_response = chatbot.generate_response(message)
    bot_message = html.Div(
        f"AI: {bot_response}",
        style={'marginBottom': '1rem', 'textAlign': 'left', 'color': '#2c3e50'}
    )
    
    history.extend([user_message, bot_message])
    return history, ''

if __name__ == '__main__':
    app.run_server(debug=True)