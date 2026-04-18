from datetime import datetime
from plyze.paths import ProjectPaths
from plyze.utils import CaseData


example_casedata = CaseData(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
example_times = [datetime(2017, 7, 1, i) for i in [1, 2, 3, 4]]
