import pytest
import pandas as pd
import textwrap
from app.services.sandbox_service import SandboxService

@pytest.fixture
def sample_dataframe():
    """Provides a sample pandas DataFrame for testing."""
    data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
    return pd.DataFrame(data)

def test_execute_code_success_with_stdout(sample_dataframe):
    """
    Tests the sandbox's ability to execute valid code that produces standard output.
    """
    # Arrange
    code = "print(df['A'].sum())"
    sandbox = SandboxService()
    
    # Act
    result = sandbox.execute_code(code, sample_dataframe)
    
    # Assert
    assert result['success'] is True
    assert result['stdout'].strip() == '6' # .strip() to remove trailing newline
    assert result['stderr'] == ''
    assert result['image'] is None

def test_execute_code_with_error(sample_dataframe):
    """
    Tests the sandbox's ability to safely handle code that raises an exception.
    """
    # Arrange
    code = "print(df['C'])"  # Column 'C' does not exist, will raise a KeyError
    sandbox = SandboxService()
    
    # Act
    result = sandbox.execute_code(code, sample_dataframe)
    
    # Assert
    assert result['success'] is False
    assert result['stdout'] == ''
    assert 'KeyError' in result['stderr']
    assert result['image'] is None

def test_execute_code_generates_plot(sample_dataframe):
    """
    Tests the sandbox's ability to execute code that generates and saves a plot.
    """
    # Arrange
    code = textwrap.dedent("""
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        df.plot(kind='bar', x='A', y='B', ax=ax)
        fig.savefig('plot.png')
        plt.close(fig)
    """)
    sandbox = SandboxService()
    
    # Act
    result = sandbox.execute_code(code, sample_dataframe)
    
    # Assert
    assert result['success'] is True
    assert result['image'] is not None
    assert isinstance(result['image'], bytes) # Check if it returns binary data
    assert len(result['image']) > 0 # Check that the image data is not empty