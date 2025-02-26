"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge  regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.rename(
        columns={
            "name": "name_dep",
            "code": "code_dep"})
    Data = pd.merge(
        regions[["code", "name"]],
        departments[["region_code", "code_dep", "name_dep"]],
        left_on="code",
        right_on="region_code",
    )
    Data.drop("region_code", axis=1, inplace=True)
    Data.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]
    return Data


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum.copy()
    for i in range(10):
        ref["Department code"].replace(str(i), "0" + str(i), inplace=True)
    Data = pd.merge(
        ref,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return Data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    Data2 = referendum_and_areas[
        [
            "code_reg",
            "name_reg",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
        ]
    ]
    Data2[["Registered", "Abstentions", "Null", "Choice A", "Choice B"]] = (
        Data2[["Registered", "Abstentions", "Null", "Choice A", "Choice B"]]
        .apply(pd.to_numeric)
    )

    Data = Data2.groupby("code_reg").agg(
        {
            c: "sum" if Data2[c].dtype == "int64" else "first"
            for c in Data2.columns
        }
    )
    Data = Data[["name_reg", "Registered",
                 "Abstentions", "Null", "Choice A", "Choice B"]]
    return Data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("data/regions.geojson")
    merged_data = pd.merge(
        referendum_result_by_regions,
        geo_data,
        left_index=True,
        right_on="code",
        how="left",
    )
    merged_data["ratio"] = merged_data["Choice A"] / (
        merged_data["Choice A"] + merged_data["Choice B"]
    )
    merged_data = gpd.GeoDataFrame(merged_data)
    merged_data.plot(column="ratio")
    return merged_data


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
