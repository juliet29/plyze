from datetime import datetime


from plys.jpg.main import idf_to_jpgraph, set_levels
from plys.utils import CaseData
from plys.paths import ProjectPaths


# TODO: move this to examples...
cd = CaseData(ProjectPaths.sample_idf, ProjectPaths.sample_sql)


def test_create_from_idf():
    jpg = idf_to_jpgraph(*cd, datetime_=datetime(2017, 7, 1, 12))
    assert len(jpg.jpnodes) > 1
    assert len(list(jpg.edges)) > 1


def test_set_levels():
    jpg = idf_to_jpgraph(*cd, datetime_=datetime(2017, 7, 1, 12))
    # TODO: modifyung in place, not very functional, could cause errors later...
    jpg = set_levels(jpg)

    levels = set([i.data.level for i in jpg.jpnodes])
    assert len(levels) > 1
