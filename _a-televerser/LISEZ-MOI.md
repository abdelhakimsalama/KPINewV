# Contenus a televerser dans Copilot Studio

**Ce dossier est genere. Ne le modifiez pas a la main.**

Chaque fichier est extrait automatiquement du bloc a copier de sa fiche d'etape, qui reste la source de verite :

| Fichier genere | Fiche source | Ou le coller |
|---|---|---|
| `instructions.md` | `04_INSTRUCTIONS/04_01_instructions-a-copier.md` | Onglet Build, editeur d'instructions |
| `skills/kpi-field-details/SKILL.md` | `05_SKILLS/05_01_skill-kpi-field-details.md` | Onglet Build, panneau Composants, Skills |
| `skills/mybi-sac-mapping/SKILL.md` | `05_SKILLS/05_02_skill-mybi-sac-mapping.md` | Onglet Build, panneau Composants, Skills |
| `skills/sac-query-lookup/SKILL.md` | `05_SKILLS/05_03_skill-sac-query-lookup.md` | Onglet Build, panneau Composants, Skills |
| `skills/business-vocabulary-and-ambiguity/SKILL.md` | `05_SKILLS/05_04_skill-business-vocabulary-and-ambiguity.md` | Onglet Build, panneau Composants, Skills |
| `skills/personas-and-scope/SKILL.md` | `05_SKILLS/05_05_skill-personas-and-scope.md` | Onglet Build, panneau Composants, Skills |

Pour modifier un contenu : editez la **fiche d'etape**, puis regenerez ce dossier avec
`python3 outils/extraire-contenus-agent.py`. Un `git diff` vide apres regeneration
prouve que le dossier est a jour.
