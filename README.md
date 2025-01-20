# Kingdom 1007 Stats Tracker

This is a Python-based web app for tracking and visualizing statistics from the Kingdom 1007 game. It ingests CSV data into an SQLite database, displays the data interactively, and provides options to filter, analyze trends, and view various game statistics like power, killpoints, and deads.

The app is built with **Streamlit**, **Altair**, **Pandas**, and **SQLite** for data management and visualization.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact](#contact)

---

## Introduction

The Kingdom 1007 Stats Tracker app allows users to upload CSV files, ingest them into a database, and visualize the game stats over time. Users can filter data by different columns, analyze trends for specific governors, and interact with a user-friendly interface built with **Streamlit**. The app also supports multi-language functionality (English and Spanish).

---

## Features

- **Data Ingestion**: Automatically reads CSV files and stores them in an SQLite database.
- **Interactive Dashboard**: Displays tables with options to filter by columns and ranges.
- **Trend Analysis**: Visualizes trends for specific game stats like power, killpoints, and deads over time.
- **Language Support**: Supports both English and Spanish for better accessibility.
- **Responsive UI**: Designed for a smooth user experience with Streamlit.

---

## Installation

### Prerequisites

Make sure you have Python 3.x installed. You will also need to install the following libraries:
- **Streamlit**: For creating the interactive web app.
- **Altair**: For creating visualizations.
- **Pandas**: For data manipulation and analysis.
- **SQLite**: For data storage (SQLite comes with Python by default).

### Step-by-Step Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/username/kingdom1007-stats-tracker.git
    ```

2. Navigate to the project directory:
    ```bash
    cd kingdom1007-stats-tracker
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

### Running the App

1. Place your CSV files in the `data/` directory. Each CSV file should be named with a date format (e.g., `10102021.csv`), as this will be used to generate the date for the data.
2. Start the Streamlit app:
    ```bash
    streamlit run app.py
    ```

3. The app will load in your web browser. Select the language (English or Spanish) from the dropdown, and the app will display an interactive table of the data. You can:
    - Choose the table for a specific date.
    - Filter data by columns (numeric or categorical).
    - Visualize trends for different game stats over time for a specific governor.

### Features in the App

- **Data Filtering**: Filters based on columns (e.g., governorID, power, killpoints).
- **Trend Visualization**: Line charts to show trends over time for selected columns.
- **Multi-language Support**: Easily switch between English and Spanish for the UI.
  
---

## Contributing

We welcome contributions to improve this project! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m "Add new feature"`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a pull request with a description of your changes.

Please ensure that your code follows the existing style and passes any tests before submitting a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For any questions or issues, feel free to contact the project maintainer:

- [GitHub Profile](https://github.com/username)
- Email: [lioneleoy@gmail.com]

---

### Additional Information

- **CSV File Structure**: Each CSV should have columns for governorID, name, power, killpoints, deads, etc. The file names should follow the format `MMDDYYYY.csv`, where MM is the month, DD is the day, and YYYY is the year.
