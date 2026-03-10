from plyze.fpviz.main import plan_plot
from plyze.paths import ProjectPaths


def test_plan_plot():
    plan_plot(ProjectPaths.sample_idf, show=False)
    assert 1
