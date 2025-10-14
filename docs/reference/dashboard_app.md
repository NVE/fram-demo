# `dashboard_app.py` script

`dashboard_app.py` sript contains outline of the dashboard for results visulaization. Dashboard is built using streamlit package in Python. 

Script `run_dashboard.py` in the demo calls upon `dashboard_app.py` and renders the dashboard in your browser:

```python
app_path = current_folder / "dashboard_app.py"
subprocess.run(["streamlit", "run", app_path, "--server.port", "5000"], check=True)
```

::: framdemo.dashboard_app


