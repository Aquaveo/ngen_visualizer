from tethys_sdk.base import TethysAppBase


class App(TethysAppBase):
    """
    Tethys app class for Ngen Visualizer.
    """

    name = 'Ngen Visualizer'
    description = 'This application allows you to visualize the outputs of your model into tethys'
    package = 'ngen_visualizer'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'ngen-visualizer'
    color = '#27ae60'
    tags = ''
    enable_feedback = False
    feedback_emails = []