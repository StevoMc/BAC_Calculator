# Alcohol Calculator

In this application, the Blood Alcohol Content (BAC) is calculated using various factors such as weight, gender, age, and the total amount of alcohol consumed. The BAC is a measure of the alcohol concentration in the bloodstream, and this app takes into account key variables to give a personalized estimate. Here's how it works:

1. **Age Factor**:
   The age factor slightly decreases the BAC estimate for users older than 20, with a gradual reduction as age increases. This is handled by the `calculate_age_factor(age)` function, which reduces the BAC by 0.1% for each year above 20.

2. **Reduction Factor (Gender and Age)**:
   The app considers gender differences in alcohol absorption rates. Men and women have different reduction factors due to differences in body composition. The function `calculate_reduction_factor(gender, age)` uses predefined reduction rates for men and women, which are then adjusted based on age.

3. **BAC Calculation**:
   The total amount of alcohol consumed is calculated in milliliters (`total_alcohol * 1000`), and then it is multiplied by an absorption rate to determine how much alcohol is absorbed by the body. The BAC is calculated using the formula:
   \[
   \text{BAC} = \frac{\text{absorbed alcohol}}{\text{weight} \times \text{reduction factor}}
   \]
   The result is rounded to three decimal places for precision.

4. **Adjusted Metabolism Rate**:
   The metabolism rate, which dictates how fast the body can process alcohol, is also influenced by age and weight. The app adjusts the metabolism rate based on the user's age (older users metabolize alcohol slightly slower) and weight (heavier users metabolize alcohol faster). The `calculate_adjusted_metabolism_rate(age, weight)` function accounts for these variables.

5. **Time to Sober**:
   Based on the current BAC and the user's adjusted metabolism rate, the app estimates how long it will take for the user to sober up. The formula:
   \[
   \text{Time to sober} = \frac{\text{BAC}}{\text{metabolism rate}}
   \]
   estimates the number of hours until the BAC returns to zero.

6. **Total Alcohol Consumption**:
   The `calculate_total_alcohol_in_liters(drinks)` function sums up the alcohol content from all drinks consumed during the session. Each drink's alcohol content is calculated using its volume and alcohol percentage.

These calculations take into account individual differences, providing a personalized BAC estimate that reflects factors like gender, age, and body weight. This approach gives users a more accurate prediction of their BAC and how long it will take for the alcohol to leave their system.

---

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Add drinks**: Input the type of drink, volume, and alcohol percentage.
- **BAC Calculation**: Estimate Blood Alcohol Content based on user inputs.
- **History Tracking**: Track all added drinks in the session.
- **Session Management**: Reset drink history and start over.
- **Custom Drink Addition**: Users can add custom drinks with specific volume and alcohol percentage.

## Technologies

- **Flask**: Web framework for the backend.
- **Flask-Session**: For session-based management.
- **Babel**: For handling date formatting.
- **Cachelib**: Caching utility for Flask.
- **HTML/CSS/JavaScript**: Frontend interface.
- **Pytest**: For running unit tests.

## Installation

### Prerequisites

- Python 3.7 or higher
- [pip](https://pip.pypa.io/en/stable/installation/) for installing dependencies.

### Step-by-Step Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/alcohol-calculator.git
   cd alcohol-calculator
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python3 run.py
   ```

   ```bash
   python3 -m flask --app alcohol_calculator run --debug --host=0.0.0.0
   ```

5. **Access the application**:

   Open a browser and navigate to `http://127.0.0.1:5000`.

## Usage

### Adding a Drink

1. Navigate to the home page.
2. Select a drink from the list or add a custom drink.
3. Enter the volume and alcohol percentage.
4. The BAC will be automatically calculated based on your user profile.

### View History

- Click on the "History" tab to view all your added drinks.
- You can reset the session history at any time.

## Running Tests

The project uses `pytest` for testing. To run tests, execute the following command:

```bash
python3 -m pytest -v tests/
```

### Tracking Print Outputs

To track print statements during testing, use the `-s` option:

```bash
python3 -m pytest -s -v tests/
```

This will display all output including `print()` statements during test execution.

## Project Structure

```plaintext
alcohol_calculator/
│
├── models/                # Data models for drinks and users
│   ├── drink.py           # Drink model
│   ├── user.py            # User model
│
├── templates/             # HTML templates for the app
│   ├── index.html         # Main page
│   ├── history.html       # History page
│
├── static/                # Static files like CSS, JS
│
├── tests/                 # Unit tests for the app
│   ├── test_alcohol_calculator.py  # Main tests
│
├── run.py                 # Main entry point for running the Flask app
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
```

## Contributing

We welcome contributions! Follow these steps to contribute:

1. Fork the repository.
2. Create a new feature branch.

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. Commit your changes.

   ```bash
   git commit -am 'Add new feature'
   ```

4. Push to the branch.

   ```bash
   git push origin feature/my-new-feature
   ```

5. Open a Pull Request.

### Coding Standards

- Follow PEP 8 for Python code.
- Use clear and descriptive commit messages.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Explanation

- **Features**: Lists the core functionality of your project.
- **Technologies**: Specifies the tech stack used.
- **Installation**: Provides clear steps for setup.
- **Usage**: Describes how to interact with the app (adding drinks, calculating BAC).
- **Running Tests**: Shows how to run unit tests, including verbose and print options.
- **Project Structure**: Gives an overview of the folder structure to help contributors.
- **Contributing**: Provides guidelines on how to contribute, including coding standards.
- **License**: Mentions the licensing.
