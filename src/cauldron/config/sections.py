from pydantic import BaseModel


class SectionConfig(BaseModel):
    name: str
    heading_pattern: str
    required: bool = True


class SectionsConfig(BaseModel):
    sections: list[SectionConfig]
