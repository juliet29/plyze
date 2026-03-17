import altair as alt

CLEARVIEW = "ClearviewText"
FONT = f'{CLEARVIEW}, system-ui, -apple-system, BlinkMacSystemFont, ".SFNSText-Regular", sans-serif'
FONT_SIZE = 14
LABEL_FONT_SIZE = 14
TITLE_FONT_SIZE = 18
FONT_COLOR = "#161616"
LABEL_COLOR = "#525252"
DEF_WIDTH = 350


@alt.theme.register("default_theme", enable=True)
def default_theme() -> alt.theme.ThemeConfig:
    return {
        "config": {
            # "view": {
            #     "width": 350,
            #     "height": 280,
            # },
            "axis": {
                "labelColor": LABEL_COLOR,
                "labelFontSize": LABEL_FONT_SIZE,
                "labelFont": FONT,
                "labelFontWeight": 400,
                "titleColor": FONT_COLOR,
                "titleFontWeight": 400,
                "titleFontSize": TITLE_FONT_SIZE,
                "titleFont": FONT,
            },
            "axisX": {"titlePadding": 10},
            "axisY": {"titlePadding": 2.5},
            "text": {"font": FONT, "fontSize": FONT_SIZE},
            "range": {},  # type: ignore
            "legend": {
                "labelFont": FONT,
                "labelFontSize": LABEL_FONT_SIZE,
                "labelLimit": 500,
            },
            "header": {
                "labelFont": FONT,
                "titleFont": FONT,
                "labelFontSize": LABEL_FONT_SIZE,
                "titleFontSize": TITLE_FONT_SIZE,
            },
        },
    }
