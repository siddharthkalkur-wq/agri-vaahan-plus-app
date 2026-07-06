import streamlit as st
import pandas as pd
import json
import time
from mistralai.client import Mistral

# Import your tools
import functions 
from functions_data_cleaning import data_cleaning
from functions_data_imputing import data_imputation
from functions_data_vis import data_visualization
from functions_time_series_models import time_series_forecasting

st.set_page_config(page_title="Agri-Vaahan LLM", page_icon="❇️")
st.title('AGRI-VAAHAN PLUS ❇️')

########################## 1. DATA UPLOAD
if 'data' not in st.session_state:
    st.session_state['data'] = None

uploaded_file = st.file_uploader("Upload CSV or XLSX file", type=['csv', 'xlsx'])
header_row = st.number_input('Select header row', min_value=0, value=0)

if uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file, header=header_row)
    else:
        df = pd.read_excel(uploaded_file, header=header_row)

    # Force a data refresh if it's a newly uploaded file
    if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
        st.session_state['data'] = df.copy()
        st.session_state["last_uploaded_file"] = uploaded_file.name
        st.success("File uploaded and data refreshed successfully!")

if st.session_state['data'] is not None:
    st.write(st.session_state['data'])

########################## 2. MISTRAL CLOUD MODEL
if "mistral_client" not in st.session_state:
    try:
        st.session_state["mistral_client"] = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
    except KeyError:
        st.error("Missing Mistral API Key! Please configure MISTRAL_API_KEY in Secrets.")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for msg in st.session_state["chat_history"]:
    # Safely extract data whether it is a standard dictionary or a Mistral Object
    role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "")
    content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
    
    # Only draw the UI for actual text messages, keeping background tool calls hidden
    if role in ["user", "assistant"] and content:
        st.chat_message(role).write(content)

prompt = st.chat_input("Query here")

if prompt and "mistral_client" in st.session_state:
    st.chat_message("user").write(prompt)
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    
    client = st.session_state["mistral_client"]
    tools = functions.get_mistral_tools()
    
    with st.spinner("Analyzing..."):
        # Format history for Mistral
        messages = []
        for m in st.session_state["chat_history"]:
            if isinstance(m, dict):
                messages.append(m)
            else:
                # Safely convert Mistral's Python objects back into network dictionaries
                msg_dict = {"role": getattr(m, "role", ""), "content": getattr(m, "content", "")}
                if getattr(m, "tool_calls", None):
                    msg_dict["tool_calls"] = m.tool_calls
                messages.append(msg_dict)
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_msg = response.choices[0].message
        
        # 3. Check if the AI wants to run a function
        if response_msg.tool_calls:
            # We add Mistral's request to run a tool to our chat history
            st.session_state["chat_history"].append(response_msg)
            
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                st.info(f"⚙️ Running automated tool: {func_name}")
                
                # Execute the correct function and capture the output
                result_df_or_val = None
                if func_name == "data_cleaning":
                    result_df_or_val = data_cleaning(**args)
                elif func_name == "data_imputation":
                    result_df_or_val = data_imputation(**args)
                elif func_name == "data_visualization":
                    result_df_or_val = data_visualization(**args)
                    # ❇️ NEW: Ensure tables from visualization actually draw on your web screen
                    if result_df_or_val is not None:
                        if isinstance(result_df_or_val, pd.DataFrame):
                            st.dataframe(result_df_or_val)
                        else:
                            st.plotly_chart(result_df_or_val)
                elif func_name == "time_series_forecasting":
                    result_df_or_val = time_series_forecasting(**args)
                
                # Convert whatever your function returns into a string message for Mistral
                if isinstance(result_df_or_val, pd.DataFrame):
                    if result_df_or_val.shape == (0, 0):
                        tool_content = "ERROR: The tool failed or returned a completely empty dataframe. Please check your parameters and try again."
                    elif func_name in ["data_visualization", "time_series_forecasting"]:
                        # ❇️ NEW: Feed the actual small summary tables directly to Mistral so it can read the numbers!
                        tool_content = f"Tool executed successfully. Here is the exact data:\n{result_df_or_val.to_string()}"
                    else:
                        # For massive dataset changes (cleaning/imputing), only send the shape to save API limits
                        tool_content = f"Tool executed successfully. Current shape of dataframe is {result_df_or_val.shape}."
                else:
                    tool_content = str(result_df_or_val)
                
                # IMPORTANT: Append the tool response back so Mistral knows it worked!
                st.session_state["chat_history"].append({
                    "role": "tool",
                    "name": func_name,
                    "content": tool_content,
                    "tool_call_id": tool_call.id
                })
            
            # ❇️ LOOP CLOSURE: Call Mistral again, passing the data results back
            with st.spinner("Formulating final agricultural advisory..."):
                final_messages = []
                for m in st.session_state["chat_history"]:
                    if isinstance(m, dict):
                        final_messages.append(m)
                    else:  # Handles Mistral native Message objects safely
                        final_messages.append({"role": m.role, "content": m.content, "tool_calls": m.tool_calls})
                
                final_response = client.chat.complete(
                    model="mistral-small-latest",
                    messages=final_messages
                )
                
                final_text = final_response.choices[0].message.content
                st.chat_message("assistant").write(final_text)
                st.session_state["chat_history"].append({"role": "assistant", "content": final_text})
                
        # If no tool is called, output standard text
        elif response_msg.content:
            st.chat_message("assistant").write(response_msg.content)
            st.session_state["chat_history"].append({"role": "assistant", "content": response_msg.content})
