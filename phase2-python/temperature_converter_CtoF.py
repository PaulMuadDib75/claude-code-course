# Temperature Converter: Celsius to Fahrenheit

# Prompt the user to enter a temperature in Celsius and store the input
celsius_str = input("Enter temperature in Celsius: ")

# Convert the string input to a floating-point number
celsius = float(celsius_str)

# Apply the conversion formula: F = (C × 9/5) + 32
fahrenheit = (celsius * 9/5) + 32

# Round the result to 2 decimal places for clean display
fahrenheit_rounded = round(fahrenheit, 2)

# Display the converted temperature to the user
print(f"{celsius}°C is equal to {fahrenheit_rounded}°F")