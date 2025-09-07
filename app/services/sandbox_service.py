import subprocess
import tempfile
import pandas as pd
import os
import sys
from typing import TypedDict, Optional

class ExecutionResult(TypedDict):
    success: bool
    stdout: str
    stderr: str
    image: Optional[bytes]


class SandboxService:
    """
    Provides a secure environment for executing AI-generated Python code.
    """
    _DF_FILENAME = 'data.pkl'
    _SCRIPT_FILENAME = 'script.py'
    _PLOT_FILENAME = 'plot.png'

    def execute_code(self, code: str, df: pd.DataFrame) -> ExecutionResult:
        """
        Executes Python code in a temporary, isolated environment.

        Args:
            code: A string containing the Python code to execute.
            df: The pandas DataFrame to be made available to the code.

        Returns:
            An ExecutionResult dictionary containing the outcome.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            df_path = os.path.join(tmpdir, self._DF_FILENAME)
            script_path = os.path.join(tmpdir, self._SCRIPT_FILENAME)
            plot_path = os.path.join(tmpdir, self._PLOT_FILENAME)

            df.to_pickle(df_path)

            full_script = f"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load the DataFrame from the provided pickle file
df = pd.read_pickle('{df_path}')

# --- AI Generated Code Start ---
{code}
# --- AI Generated Code End ---
"""
            with open(script_path, 'w') as f:
                f.write(full_script)

            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=tmpdir
            )

            image_data: Optional[bytes] = None
            if os.path.exists(plot_path):
                with open(plot_path, 'rb') as f:
                    image_data = f.read()

            return ExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                image=image_data,
            )

sandbox_service = SandboxService()

