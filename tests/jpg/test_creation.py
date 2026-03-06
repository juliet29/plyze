from pathlib import Path
import tempfile
from datetime import datetime

from plys.jpg.interfaces import JPGraphModel
from plys.jpg.main import idf_to_jpgraph, set_levels
from plys.paths import ProjectPaths
from plys.utils import CaseData

# TODO: move this to examples...


class TestJPGCreation:
    cd = CaseData(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
    graph_name = "sample"

    datetime = datetime(2017, 7, 1, 12)

    def test_create_from_idf(self):
        jpg = idf_to_jpgraph(self.graph_name, *self.cd, self.datetime)
        assert len(jpg.jpnodes) > 1
        assert len(list(jpg.edges)) > 1

    @property
    def G(self):
        return idf_to_jpgraph(self.graph_name, *self.cd, self.datetime)

    def test_set_levels(self):
        # TODO: modifyung in place, not very functional, could cause errors later...
        jpg = set_levels(self.G)

        levels = set([i.data.level for i in jpg.jpnodes])
        assert len(levels) > 1

    def test_io(self):
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td) / "out.json"
            JPGraphModel.write(self.G, tpath)
            res = JPGraphModel.read(tpath)
            assert len(res.jpnodes) > 1
            assert len(res.jpedges) > 1
