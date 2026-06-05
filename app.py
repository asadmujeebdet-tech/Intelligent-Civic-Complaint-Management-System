"""Use run_server.py instead:  streamlit run run_server.py"""
import sys

if "streamlit" in sys.modules:
    import runpy

    runpy.run_path("run_server.py", run_name="__main__")
elif __name__ == "__main__":
    import runpy

    runpy.run_path("run_server.py", run_name="__main__")
