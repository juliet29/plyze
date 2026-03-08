import altair as alt


class AltairRenderers:
    BROWSER = "browser"

    @classmethod
    def set_renderer(cls):
        alt.renderers.enable(cls.BROWSER)
