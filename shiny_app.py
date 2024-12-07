from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Define the UI layout with checkbox group for selecting years and races
app_ui = ui.page_fluid(
    ui.input_checkbox_group(id='year', label='Choose a year:', choices=["2010", "2020"], 
                            selected=["2010", "2020"]),
    ui.output_plot('income_value'),  # Plot for income vs house value
    ui.input_checkbox_group(id="race", label="Choose a Category:", choices=[
        "Non-Hispanic White", "Black", "Hispanic", "Asian"]),
    ui.output_plot('rent_affordability')  # Plot for rent affordability
)

# Define server
def server(input, output, session):
    
    # Reactive function to load and return the full dataset for income vs house value
    @reactive.Calc
    def full_data():
        df = pd.read_csv("ZHVI_MHI.csv")  # Dataset for income and house value
        return df
    
    # Reactive function to load and return the rent data
    @reactive.Calc
    def rent_data():
        df = pd.read_csv("zori_median_income.csv")  # Dataset for rent affordability by race
        return df
    
    # Reactive function to filter the data based on the selected years (first plot)
    @reactive.Calc
    def subsetted_data():
        df = full_data()
        selected_years = input.year()

        columns_to_select = []
        for year in selected_years:
            income_column = f'Med_Income_{year}'
            house_value_column = f'house_value_{year}'

            if income_column in df.columns and house_value_column in df.columns:
                columns_to_select.append((income_column, house_value_column))

        return df, columns_to_select

    # Reactive function to filter the rent affordability data based on selected races (for the second plot)
    @reactive.Calc
    def filtered_rent_data():
        df = rent_data()
        selected_races = input.race()
        
        # Always include 'total' in the plot
        race_columns = ['All']
        
        # Add selected races to the list of columns to overlay
        for selected_race in selected_races:
            if selected_race == "Non-Hispanic White":
                race_columns.append("NH_White")
            elif selected_race == "Black":
                race_columns.append("Black")
            elif selected_race == "Asian":
                race_columns.append("Asian")
            elif selected_race == "Hispanic":
                race_columns.append("Hispanic")
        
        return df, race_columns  # Ensure to return both df and race_columns    

    # Render the first plot (income vs house value)
    @render.plot
    def income_value():
        df, selected_columns = subsetted_data()
        
        if not selected_columns:
            print("No data to plot!")  # Debugging line
            return None
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot the data for each selected year
        for income_column, house_value_column in selected_columns:
            ax.scatter(df[income_column], df[house_value_column], label=f'{income_column.split("_")[2]}')

        ax.set_xlabel('Median Household Income ($)')
        ax.set_ylabel('House Value Index ($)')
        ax.set_title('Median Household Income vs. Home Values')

        # Format the y-axis and x-axis labels with commas for readability
        def currency_format(x, pos):
            return f"${x:,.0f}"

        ax.yaxis.set_major_formatter(FuncFormatter(currency_format))
        ax.xaxis.set_major_formatter(FuncFormatter(currency_format))
        
        # Show the legend
        ax.legend()
        
        return fig
    
    # Render the second plot (rent affordability by race)
    @render.plot
    def rent_affordability():
        df, race_columns = filtered_rent_data()

        if df.empty:
            print("No data to plot!")  # Debugging line
            return None
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Always plot the Rent line
        ax.plot(df['year'], df['Rent'], label='Mean Rent', color='blue', linewidth=2)
        
        # Plot additional lines for each selected race
        for race_column in race_columns:
            ax.plot(df['year'], df[race_column], label=f'Affordable Rent for Median {race_column} Renter', linestyle='--', linewidth=2)

        ax.set_xlabel('Year')
        ax.set_ylabel('Median Monthly Household Income')
        ax.set_title(f'Rent Affordability Over Time')

        # Format the y-axis for readability
        def currency_format(x, pos):
            return f"${x:,.0f}"

        ax.yaxis.set_major_formatter(FuncFormatter(currency_format))

        # Show the legend
        ax.legend()

        return fig

# Create the app object
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()