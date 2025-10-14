def demo_8_run_dashboard():
    """Runs dashboard with results in your browser.
    
    1. Finds an available port on localhost.
    2. Makes sure a supported browser is available (chrome, msedge or firefox).
    2. Runs streamlit dashboard by data and plots in dashboard_app.py.
    """
    import subprocess
    import webbrowser
    from pathlib import Path
    from os import environ

    def get_available_port() -> int:
        """
        Find an available local port by binding to port 0.

        The operating system will assign a free port.
        """
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))  # Binds to an available port on all interfaces
            return int(s.getsockname()[1])  # Returns the assigned port number

    def get_streamlit_cmd_path() -> Path | None:
        """Search sys.path and return first path to streamlit.cmd."""
        import sys
        from collections.abc import Iterable

        def _get_streamlit_cmd_path(paths: Iterable[Path]) -> Path | None:
            for path in paths:
                if not path.is_dir() and path.name.lower() == "streamlit.cmd":
                    return path
                if path.is_dir():
                    result = _get_streamlit_cmd_path(path.iterdir())
                    if result is not None:
                        return result
            return None

        return _get_streamlit_cmd_path(map(Path, sys.path))

    def get_browser_exe_path() -> Path:
        """Find a browser supported by streamlit."""
        import browsers

        # safari is also supported by streamlit, but not findable with pybrowsers it seems
        findable_and_supported_by_streamlit = ["chrome", "msedge", "firefox"]

        browser_dicts = list(browsers.browsers())

        browser_dicts = [d for d in browser_dicts if d["browser_type"] in findable_and_supported_by_streamlit]

        if not browser_dicts:
            message = "Was not able to automatically find a supported browser. Need chrome, msedge or firefox to run."
            raise RuntimeError(message)

        return browser_dicts[0]["path"]

    current_folder = Path.resolve(Path(__file__)).parent
    app_path = current_folder / "dashboard_app.py"

    port = get_available_port()

    # Open the Streamlit app in browser
    webbrowser.register("streamlit_browser", None, webbrowser.BackgroundBrowser(get_browser_exe_path()))

    # Used to avoid email prompt on first run
    environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # Run the Streamlit app
    streamlit_cmd_path = get_streamlit_cmd_path()
    streamlit_cmd = "streamlit" if streamlit_cmd_path is None else str(streamlit_cmd_path)
    subprocess.run([streamlit_cmd, "run", str(app_path), "--server.port", str(port)], check=True)


if __name__ == "__main__":
    demo_8_run_dashboard()
