import json
from pathlib import Path
import pandas as pd
from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller
from .app import App as app


MODEL_OUTPUT_FOLDER_NAME = "ngen-data"


@controller(name="home", app_workspace=True)
class MapLayoutTutorialMap(MapLayout):
    app = app
    base_template = "ngen_visualizer/base.html"
    basemaps = ["OpenStreetMap", "ESRI", "Stamen"]
    map_title = "Next Gen in a Box Visualizer"
    map_subtitle = "NOAA-OWP NextGen Model Outputs"
    # default_map_extent = [
    #     -87.83371926334216,
    #     33.73443611122197,
    #     -86.20833410475134,
    #     34.456557011634175,
    # ]
    # max_zoom = 14
    # min_zoom = 9
    show_properties_popup = True
    plot_slide_sheet = True

    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        """
        Add layers to the MapLayout and create associated layer group objects.
        """
        # Load GeoJSON from files
        config_directory = (
            Path(app_workspace.path) / MODEL_OUTPUT_FOLDER_NAME / "config"
        )

        # Nexus Points
        nexus_path = config_directory / "nexus.geojson"
        with open(nexus_path) as nf:
            nexus_geojson = json.loads(nf.read())

        nexus_layer = self.build_geojson_layer(
            geojson=nexus_geojson,
            layer_name="nexus",
            layer_title="Nexus",
            layer_variable="nexus",
            visible=True,
            selectable=True,
            plottable=True,
        )

        # Catchments
        catchments_path = config_directory / "catchments.geojson"
        with open(catchments_path) as cf:
            catchments_geojson = json.loads(cf.read())

        catchments_layer = self.build_geojson_layer(
            geojson=catchments_geojson,
            layer_name="catchments",
            layer_title="Catchments",
            layer_variable="catchments",
            visible=True,
            selectable=True,
            plottable=True,
        )

        # Create layer groups
        layer_groups = [
            self.build_layer_group(
                id="nextgen-features",
                display_name="NextGen Features",
                layer_control="checkbox",  # 'checkbox' or 'radio'
                layers=[
                    nexus_layer,
                    catchments_layer,
                ],
            )
        ]

        return layer_groups

    @classmethod
    def get_vector_style_map(cls):
        return {
            "Point": {
                "ol.style.Style": {
                    "image": {
                        "ol.style.Circle": {
                            "radius": 5,
                            "fill": {
                                "ol.style.Fill": {
                                    "color": "white",
                                }
                            },
                            "stroke": {"ol.style.Stroke": {"color": "red", "width": 3}},
                        }
                    }
                }
            },
            "MultiPolygon": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": "navy", "width": 3}},
                    "fill": {"ol.style.Fill": {"color": "rgba(0, 25, 128, 0.1)"}},
                }
            },
        }

    def get_plot_for_layer_feature(
        self,
        request,
        layer_name,
        feature_id,
        layer_data,
        feature_props,
        app_workspace,
        *args,
        **kwargs,
    ):
        """
        Retrieves plot data for given feature on given layer.

        Args:
            layer_name (str): Name/id of layer.
            feature_id (str): ID of feature.
            layer_data (dict): The MVLayer.data dictionary.
            feature_props (dict): The properties of the selected feature.

        Returns:
            str, list<dict>, dict: plot title, data series, and layout options, respectively.
        """
        output_directory = (
            Path(app_workspace.path) / MODEL_OUTPUT_FOLDER_NAME / "outputs"
        )

        # Get the feature id
        id = feature_props.get("toid").split("_")[-1]

        # Nexus
        if layer_name == "nexus":
            layout = {"yaxis": {"title": "Streamflow (cfs)"}}

            output_path = output_directory / f"catch_{id}.csv"
            if not output_path.exists():
                print(f"WARNING: no such file {output_path}")
                return f'No Data Found for Nexus "{id}"', [], layout

            # Parse with Pandas
            df = pd.read_csv(output_path)
            time_col = df.iloc[:, 1]
            streamflow_cms_col = df.iloc[:, 2]
            sreamflow_cfs_col = streamflow_cms_col * 35.314  # Convert to cfs
            data = [
                {
                    "name": "Streamflow",
                    "mode": "lines",
                    "x": time_col.tolist(),
                    "y": sreamflow_cfs_col.tolist(),
                    "line": {"width": 2, "color": "blue"},
                },
            ]

            return f'Streamflow at Nexus "{id}"', data, layout

        # Catchments
        else:
            layout = {"yaxis": {"title": "Evapotranspiration (mm/hr)"}}

            output_path = output_directory / f"{id}.csv"
            if not output_path.exists():
                print(f"WARNING: no such file {output_path}")
                return f'No Data Found for Catchment "{id}"', [], layout

            # Parse with Pandas
            df = pd.read_csv(output_path)
            data = [
                {
                    "name": "Evapotranspiration",
                    "mode": "lines",
                    "x": df.iloc[:, 1].tolist(),
                    "y": df.iloc[:, 2].tolist(),
                    "line": {"width": 2, "color": "red"},
                },
            ]

            return f'Evapotranspiration at Catchment "{id}"', data, layout
