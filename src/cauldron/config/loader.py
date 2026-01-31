from pathlib import Path

import yaml

from cauldron.config.sections import SectionsConfig


def load_sections_config(path: str | Path) -> SectionsConfig:
    path = Path(path)
    with path.open() as f:
        data = yaml.safe_load(f)
    return SectionsConfig.model_validate(data)
