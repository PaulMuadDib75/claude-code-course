# Temperature Converter: Fahrenheit to Celsius

# Prompt the user to enter a temperature in Fahrenheit and store the input
fahrenheit_str = input("Enter temperature in Fahrenheit: ")

# Convert the string input to a floating-point number
fahrenheit = float(fahrenheit_str)

# Apply the conversion formula: C = (F - 32) * 5/9
celsius = (fahrenheit - 32) * 5 / 9

# Round the result to 2 decimal places for clean display
celsius_rounded = round(celsius, 2)

# Display the converted temperature to the user
print(f"{fahrenheit}°F is equal to {celsius_rounded}°C")
