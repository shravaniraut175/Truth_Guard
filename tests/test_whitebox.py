from backend.core.whitebox import calculate_whitebox_score

text = """
The Eiffel Tower was built in 1750.
"""

result = calculate_whitebox_score(text)

print("\nWhite-Box UQ Result:")
print(result)