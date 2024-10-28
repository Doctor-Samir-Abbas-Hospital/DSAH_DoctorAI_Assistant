import os
import streamlit.components.v1 as components

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "chat_input_widget",
        url="https://chatinputwidgetcomponent.onrender.com",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("chat_input_widget", path=build_dir)

def chat_input_widget(key=None):
    component_value = _component_func(key=key, default={})
    return component_value
