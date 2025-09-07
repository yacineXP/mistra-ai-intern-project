import re
from mistralai.client import MistralClient
from app.core.config import settings

class AnalysisService:
    """
    A service to interact with the Mistral AI for generating data analysis code.
    """
    def __init__(self):
        """
        Initializes the Mistral AI client.
        """
        try:
            self.client = MistralClient(api_key=settings.MISTRAL_API_KEY)
        except Exception as e:
            print(f"Error initializing MistralClient: {e}")
            self.client = None

    def _is_valid_code(self, code: str) -> bool:
        """
        A simple heuristic to validate if the generated text is likely Python code.
        """
        code_keywords = ["import pandas", "import matplotlib", "df.", "print("]
        return any(keyword in code for keyword in code_keywords)

    def generate_analysis_code(self, question: str, schema: dict) -> str:
        """
        Generates Python code to answer a question based on a DataFrame schema.
        """
        if not self.client:
            raise ConnectionError("Mistral AI client is not initialized.")

        schema_str = "\n".join([f"- {col} ({dtype})" for col, dtype in schema.items()])

        system_prompt = f"""
You are an expert Python data analyst.
Your task is to write a Python script using the pandas library to answer a question about a given DataFrame.

You will be provided with the DataFrame's schema and a user's question.
The DataFrame is available in a variable named `df`.

**Rules:**
1.  **To output a text or table result, you MUST use the `print()` function.** The final line of your code must be a print statement (e.g., `print(df.head())`). Simply stating a variable name on the last line will produce no output.
2.  Do not print any intermediate steps or explanations, only the final result.
3.  If the question requires a plot, use `matplotlib.pyplot`. Save the plot to a file named 'plot.png'. **Do not** use `plt.show()` and **do not** print anything.
4.  Only use the `df` variable. Do not attempt to load data or access files.
5.  Your response must be ONLY the Python code, with no explanations or markdown.
6.  Write each Python command on a new line. Do not use semicolons to chain commands.
7.  **Crucially: If the user's question is not a data analysis query, is nonsensical, or cannot be answered with the given schema, your ONLY response must be the single word: INVALID**

**DataFrame Schema:**
{schema_str}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        try:
            chat_response = self.client.chat(
                model="mistral-large-latest",
                messages=messages,
            )
            
            raw_content = chat_response.choices[0].message.content.strip()
            code_match = re.search(r"```python\n(.*?)\n```", raw_content, re.DOTALL)
            
            generated_code = ""
            if code_match:
                generated_code = code_match.group(1).strip()
            else:
                generated_code = raw_content

            if not self._is_valid_code(generated_code):
                error_message = (
                    "I was unable to generate analysis code for your request. "
                    "Please try rephrasing your question to be more specific to your data.\n\n"
                    f"--- Model's Raw Response ---\n{generated_code}"
                )
                raise ValueError(error_message)

            return generated_code

        except ValueError as ve:
            raise ve
        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Mistral AI: {e}") from e


analysis_service = AnalysisService()

