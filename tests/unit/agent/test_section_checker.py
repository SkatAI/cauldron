from cauldron.agent.nodes.section_checker import check_sections
from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ErrorCode


def test_all_sections_present(sections_config, valid_markdown):
    state = ValidationState(content=valid_markdown)
    result = check_sections(state, config=sections_config)
    assert result["section_errors"] == []


def test_missing_sections(sections_config):
    content = "# Un titre quelconque\nAucune section requise ici."
    state = ValidationState(content=content)
    result = check_sections(state, config=sections_config)
    errors = result["section_errors"]
    assert len(errors) == len(sections_config.sections)
    assert all(e.code == ErrorCode.MISSING_SECTION for e in errors)


def test_empty_content(sections_config):
    state = ValidationState(content="")
    result = check_sections(state, config=sections_config)
    errors = result["section_errors"]
    assert len(errors) == len(sections_config.sections)


def test_heading_level_variations(sections_config):
    """Headings at ### level with bold markers should still be matched."""
    content = """\
## Contexte de l'entretien
Texte.

## PROFIL PERSONNEL

### Résumé du profil
Texte.

### Donneés sociodemographiques
Texte.

### **PARCOURS ACADÉMIQUE**
Texte.

### Style de Langage et d'Expression
Texte.

### **Méthode de Réflexion et d'Argumentation**
Texte.

## Rapport avec l'intelligence Artificielle

### **TYPES D'USAGES ACADÉMIQUES**
Texte.

### **PERCEPTION DE L'OUTIL**
Texte.

### **RAPPORT PSYCHOLOGIQUE AUX OUTILS IA**
Texte.

### **PROJECTION ET VISION D'AVENIR**
Texte.

## Instructions pour l'entretien
Texte.
"""
    state = ValidationState(content=content)
    result = check_sections(state, config=sections_config)
    assert result["section_errors"] == []


def test_partial_sections_reports_missing(sections_config):
    """Only some sections present — errors should be reported for the missing ones."""
    content = """\
## Contexte de l'entretien
Texte.

## PROFIL PERSONNEL

### Résumé du profil
Texte.

## Instructions pour l'entretien
Texte.
"""
    state = ValidationState(content=content)
    result = check_sections(state, config=sections_config)
    errors = result["section_errors"]
    # 9 total sections - 4 present = 5 missing
    assert len(errors) == 5
    missing_names = {e.message for e in errors}
    assert all("est manquante" in name for name in missing_names)
