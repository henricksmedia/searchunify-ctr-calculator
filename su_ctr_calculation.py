#!/usr/bin/env python3
"""
===============================================================================
Script Name: su_ctr_calculation.py
Description:
    This script enhances the reporting capabilities of SearchUnify by processing
    session data from a CSV file to calculate Click-Through Rates (CTR) at the
    product filter level. SearchUnify provides robust search analytics, but its
    native reporting may lack granular insights into how users interact with
    specific product filters during search sessions. This script addresses this gap
    by offering detailed CTR metrics per product, enabling stakeholders to better
    understand user engagement and optimize product visibility.

    The script performs the following tasks:
    1. Loads and cleans session data, ensuring consistency in text and datetime formats.
    2. Assigns product values to click events within sessions, preserving original
       facet data for accuracy.
    3. Filters data to focus on valid product-related interactions.
    4. Calculates CTR per product, including total sessions, sessions with clicks,
       and the resulting CTR percentage.
    5. Outputs results to a timestamped CSV file for easy integration into reporting workflows.

    By providing these granular insights, the script empowers teams to make data-driven
    decisions about product prioritization, search result relevance, and user experience
    improvements, offering a significant enhancement over SearchUnify's standard reporting.

Version: 1.0.0
Author: Jeremy Henricks
Contact: jeremy.henricks@example.com
Last Updated: 2025-02-12
===============================================================================
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import pandas as pd
import numpy as np
import datetime
import logging
import os
import sys
import tkinter as tk
from tkinter import filedialog

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Opt in to the future behavior for downcasting to prevent FutureWarnings.
pd.set_option('future.no_silent_downcasting', True)

# Configure logging to output to both file and console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ctr_calculation.log"),
        logging.StreamHandler()
    ]
)

# ---------------------------------------------------------------------------
# Function Definitions
# ---------------------------------------------------------------------------
def load_and_clean_data(input_csv):
    """
    Load and Clean Data

    Reads a CSV file with session data, converts all text columns to strings,
    trims whitespace, and converts the "Activity Time" column to datetime (if available).

    Args:
        input_csv (str): The path to the input CSV file.

    Returns:
        pd.DataFrame: The cleaned data frame.
    """
    try:
        df = pd.read_csv(input_csv, dtype=str)
    except Exception as e:
        logging.error("Error reading CSV file: %s", e)
        raise

    # Trim whitespace from all object-type columns.
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    # Convert "Activity Time" to datetime if the column exists.
    if "Activity Time" in df.columns:
        df["Activity Time"] = pd.to_datetime(df["Activity Time"], errors="coerce")
    else:
        logging.warning("Column 'Activity Time' not found; skipping datetime conversion.")
    return df

def assign_products(df):
    """
    Ensure Clicks Have Assigned Products

    Preserves the original facet values and types, sorts the data by session and time,
    fills in missing product values within each session, and ensures that for click events
    with a valid product, the facet type is set to "Product".

    Args:
        df (pd.DataFrame): The input data frame.

    Returns:
        pd.DataFrame: The data frame with assigned product values.
    """
    required_columns = ["Session Identifier", "Activity Time", "Facet Value", "Activity Type", "Facet Type"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' is missing.")

    # Preserve original facet data.
    df["Original Facet Value"] = df["Facet Value"]
    df["Original Facet Type"] = df["Facet Type"]

    # Sort events by Session Identifier and Activity Time.
    df.sort_values(by=["Session Identifier", "Activity Time"], inplace=True)

    # Replace empty strings with NaN for proper filling.
    df["Facet Value"] = df["Facet Value"].replace("", np.nan)

    # Forward-fill then backward-fill within each session.
    df["Facet Value"] = df.groupby("Session Identifier")["Facet Value"]\
                          .transform(lambda x: x.ffill().bfill().infer_objects(copy=False))

    # For click events with a valid product, force Facet Type to "Product".
    df.loc[(df["Activity Type"] == "Clicked Search Result") & (df["Facet Value"].notna()), "Facet Type"] = "Product"

    # Log any sessions where click events still lack a valid product.
    missing_product_sessions = df[
        (df["Activity Type"] == "Clicked Search Result") & (df["Facet Value"].isna())
    ]["Session Identifier"].unique()
    if len(missing_product_sessions) > 0:
        logging.error("Sessions with Clicked Search Result events with no valid Facet Value: %s",
                      missing_product_sessions)
        error_df = df[
            (df["Session Identifier"].isin(missing_product_sessions)) &
            (df["Activity Type"] == "Clicked Search Result")
        ]
        error_df.to_csv("error_report.csv", index=False)

    return df

def filter_product_data(df):
    """
    Filter for Product-related Data

    Determines valid product names from the original data (where Facet Type was "Product")
    and retains only the rows where the (backfilled) Facet Value is a valid product.

    Args:
        df (pd.DataFrame): The input data frame.

    Returns:
        pd.DataFrame: The filtered data frame containing only product-related data.
    """
    if "Original Facet Type" not in df.columns or "Original Facet Value" not in df.columns:
        raise ValueError("Original Facet Type/Value columns are missing from data.")

    valid_products = df[df["Original Facet Type"] == "Product"]["Original Facet Value"].unique()
    filtered_df = df[df["Facet Value"].isin(valid_products)].copy()
    logging.info("Filtered data to %d rows with valid product Facet Values.", len(filtered_df))
    return filtered_df

def calculate_ctr(df):
    """
    Calculate CTR per Product

    For each product, calculates:
      - Total unique sessions.
      - Unique sessions with at least one "Clicked Search Result" event.
      - The CTR as a percentage.

    Args:
        df (pd.DataFrame): The filtered data frame containing product-related events.

    Returns:
        pd.DataFrame: A data frame with columns for Product, Total Sessions, Sessions With Clicks, and CTR (%).
    """
    sessions_total = df.groupby("Facet Value")["Session Identifier"].nunique()\
                        .reset_index(name="Total Sessions")

    click_df = df[df["Activity Type"] == "Clicked Search Result"]
    sessions_with_clicks = click_df.groupby("Facet Value")["Session Identifier"].nunique()\
                                   .reset_index(name="Sessions With Clicks")

    merged = pd.merge(sessions_total, sessions_with_clicks, on="Facet Value", how="left")
    merged["Sessions With Clicks"] = merged["Sessions With Clicks"].fillna(0).astype(int)

    merged["CTR (%)"] = np.where(
        merged["Total Sessions"] > 0,
        (merged["Sessions With Clicks"] / merged["Total Sessions"] * 100).round(2),
        0.0
    )
    merged["CTR (%)"] = merged["CTR (%)"].astype(str) + "%"

    merged.rename(columns={"Facet Value": "Product"}, inplace=True)
    merged = merged[["Product", "Total Sessions", "Sessions With Clicks", "CTR (%)"]]
    return merged

def save_output(df, input_csv):
    """
    Generate Output CSV

    Saves the provided data frame to a timestamped CSV file in the same directory as the input file.

    Args:
        df (pd.DataFrame): The data frame with CTR results.
        input_csv (str): The path to the original input CSV file.

    Returns:
        str: The filename of the output CSV.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    input_dir = os.path.dirname(os.path.abspath(input_csv))
    output_filename = os.path.join(input_dir, f"ctr_output_{timestamp}.csv")
    df.to_csv(output_filename, index=False)
    logging.info("CTR calculation complete. Output saved to: %s", output_filename)
    return output_filename

def main():
    """
    Main Entry Point

    Uses a Tkinter file dialog to select the CSV file, then sequentially processes the data:
      1. Load and clean the data.
      2. Assign products to sessions.
      3. Filter for valid product data.
      4. Calculate the CTR per product.
      5. Save the output to a timestamped CSV file.
    """
    root = tk.Tk()
    root.withdraw()
    input_csv = filedialog.askopenfilename(
        title="Select the CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if not input_csv:
        logging.error("No file selected. Exiting the program.")
        sys.exit(1)

    logging.info("Selected file: %s", input_csv)
    logging.info("Starting CTR calculation process...")

    df = load_and_clean_data(input_csv)
    df = assign_products(df)
    product_df = filter_product_data(df)
    ctr_results = calculate_ctr(product_df)
    save_output(ctr_results, input_csv)

# ---------------------------------------------------------------------------
# Script Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
