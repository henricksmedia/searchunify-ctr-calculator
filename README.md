# CTR Calculation Script for SearchUnify Session Reports

## Overview

The `su_ctr_calculation.py` script enhances the reporting capabilities of [SearchUnify](https://www.searchunify.com/), a powerful search analytics platform, by providing granular Click-Through Rate (CTR) metrics at the product filter level. While SearchUnify offers robust analytics, its native reporting may not provide detailed insights into user interactions with specific product filters during search sessions. This script addresses this gap by processing session data from a CSV file to calculate CTR per product, enabling stakeholders to better understand user engagement, optimize product visibility, and make data-driven decisions.

The script performs the following tasks:
1. Loads and cleans session data, ensuring consistency in text and datetime formats.
2. Assigns product values to click events within sessions, preserving original facet data for accuracy.
3. Filters data to focus on valid product-related interactions.
4. Calculates CTR per product, including total sessions, sessions with clicks, and the resulting CTR percentage.
5. Outputs results to a timestamped CSV file for seamless integration into reporting workflows.

This tool is particularly valuable for teams seeking to improve search result relevance, prioritize product offerings, and enhance user experience based on precise analytics. For more details on SearchUnify's session reporting capabilities, refer to the [SearchUnify Session Reports Documentation](https://docs.searchunify.com/Content/Search-Analytics/Search-Analytics.htm).

## Features

- **Granular CTR Analysis**: Calculates CTR for each product filter, providing insights not readily available in SearchUnify's standard reports.
- **Data Integrity**: Preserves original facet data and handles missing values through forward- and backward-filling within sessions.
- **Error Handling**: Logs sessions with invalid click events to an error report for troubleshooting.
- **User-Friendly Interface**: Uses a Tkinter file dialog for easy CSV file selection.
- **Flexible Output**: Generates timestamped CSV files for compatibility with reporting tools.

## Prerequisites

To run the script, ensure you have the following:

- **Python**: Version 3.6 or higher.
- **Dependencies**:
  - `pandas`: For data manipulation and CSV processing.
  - `numpy`: For numerical operations.
  - `tkinter`: For the file selection dialog (typically included with Python standard library).
- **Input CSV File**: A SearchUnify session data export in CSV format with the following required columns:
  - `Session Identifier`
  - `Activity Time`
  - `Facet Value`
  - `Activity Type`
  - `Facet Type`

For guidance on exporting session data from SearchUnify, see the [Session Reports Documentation]([https://docs.searchunify.com/docs/analytics/session-reports](https://docs.searchunify.com/Content/Search-Analytics/Download-or-Share-Report.htm)).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/searchunify-ctr-calculator.git
   cd searchunify-ctr-calculator
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install pandas numpy
   ```

4. **Verify Tkinter**:
   Tkinter is usually included with Python. To confirm, run:
   ```bash
   python3 -c "import tkinter"
   ```
   If you encounter an error, install Tkinter (e.g., on Ubuntu: `sudo apt-get install python3-tk`).

## Usage

1. **Prepare the Input CSV**:
   Ensure your SearchUnify session data CSV contains the required columns listed in the Prerequisites section. Refer to [SearchUnify's Session Reports Documentation](https://docs.searchunify.com/docs/analytics/session-reports) for instructions on exporting session data.

2. **Run the Script**:
   ```bash
   python3 ctr_calculation.py
   ```

3. **Select the CSV File**:
   A file dialog will appear. Navigate to and select your input CSV file.

4. **Review Output**:
   - The script processes the data and generates a timestamped CSV file (e.g., `ctr_output_20250526_111755.csv`) in the same directory as the input file.
   - The output CSV contains:
     - `Product`: The product filter name.
     - `Total Sessions`: Number of unique sessions for the product.
     - `Sessions With Clicks`: Number of unique sessions with at least one click.
     - `CTR (%)`: Click-Through Rate as a percentage.

5. **Check Logs**:
   - A `ctr_calculation.log` file is created in the working directory, logging the process and any errors.
   - If click events lack valid product data, an `error_report.csv` file is generated for debugging.

## Example Output

For an input CSV with session data, the output CSV might look like:

```csv
Product,Total Sessions,Sessions With Clicks,CTR (%)
Product A,100,25,25.00%
Product B,50,10,20.00%
Product C,75,15,20.00%
```

## Troubleshooting

- **Missing Columns**: Ensure the input CSV has all required columns. The script will raise an error if any are missing.
- **Invalid Data**: Check `error_report.csv` if some click events lack product data.
- **Tkinter Issues**: Verify Tkinter is installed or run the script in an environment with GUI support.
- **Log Review**: Consult `ctr_calculation.log` for detailed error messages.
- **Export Issues**: If the CSV export from SearchUnify is incomplete, review the [Session Reports Documentation](https://docs.searchunify.com/docs/analytics/session-reports) for proper export procedures.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License. Copyright (c) 2025 Jeremy Henricks. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, reach out to Jeremy Henricks at [jeremy.henricks@example.com](mailto:jeremy.henricks@example.com). For additional support with SearchUnify, visit the [SearchUnify Support Portal](https://support.searchunify.com/).

---
*Last Updated: May 26, 2025*
