from pathlib import Path
from zensols.pybuild import SetupUtil

su = SetupUtil(
    setup_path=Path(__file__).parent.absolute(),
    name="zensols.mednlp",
    package_names=['zensols', 'resources'],
    package_data={'': ['*.conf', '*.json', '*.yml', '*.txt']},
    description='A natural language medical domain parsing library.',
    user='plandes',
    project='mednlp',
    keywords=['tooling'],
).setup()
