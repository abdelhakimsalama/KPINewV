#!/usr/bin/env python3
"""Extrait les contenus destines a Copilot Studio depuis les fiches d'etape.

Source de verite : les blocs de code des fiches 04_01 et 05_01..05_05.
Sortie          : _a-televerser/ (regenere a chaque execution, jamais edite a la main).

Usage :  python3 outils/extraire-contenus-agent.py [--verifier]
  sans option : regenere les fichiers
  --verifier  : echoue si les fichiers generes different des fiches (pour un controle rapide)
"""
import re, sys, pathlib, difflib

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / "_a-televerser"

FICHES_SKILLS = [
    "05_SKILLS/05_01_skill-kpi-field-details.md",
    "05_SKILLS/05_02_skill-mybi-sac-mapping.md",
    "05_SKILLS/05_03_skill-sac-query-lookup.md",
    "05_SKILLS/05_04_skill-business-vocabulary-and-ambiguity.md",
    "05_SKILLS/05_05_skill-personas-and-scope.md",
]
FICHE_INSTRUCTIONS = "04_INSTRUCTIONS/04_01_instructions-a-copier.md"

BLOC = re.compile(r"```(\w*)\n(.*?)```", re.S)


def blocs(chemin):
    return [(lang, corps) for lang, corps in BLOC.findall((RACINE / chemin).read_text())]


def contenu_instructions():
    for lang, corps in blocs(FICHE_INSTRUCTIONS):
        if lang == "markdown":
            return corps.rstrip() + "\n"
    raise SystemExit(f"Bloc markdown introuvable dans {FICHE_INSTRUCTIONS}")


def contenu_skill(fiche):
    yaml = body = None
    for lang, corps in blocs(fiche):
        if lang == "yaml" and yaml is None:
            yaml = corps.strip()
        elif lang == "markdown" and body is None:
            body = corps.rstrip()
    if not yaml or not body:
        raise SystemExit(f"Bloc yaml ou markdown introuvable dans {fiche}")
    nom = re.search(r"^name:\s*(\S+)", yaml, re.M).group(1)
    return nom, f"{yaml}\n\n{body}\n"


def attendus():
    fichiers = {"instructions.md": contenu_instructions()}
    for fiche in FICHES_SKILLS:
        nom, contenu = contenu_skill(fiche)
        fichiers[f"skills/{nom}/SKILL.md"] = contenu
    fichiers["LISEZ-MOI.md"] = (
        "# Contenus a televerser dans Copilot Studio\n\n"
        "**Ce dossier est genere. Ne le modifiez pas a la main.**\n\n"
        "Chaque fichier est extrait automatiquement du bloc a copier de sa fiche d'etape, "
        "qui reste la source de verite :\n\n"
        "| Fichier genere | Fiche source | Ou le coller |\n|---|---|---|\n"
        "| `instructions.md` | `04_INSTRUCTIONS/04_01_instructions-a-copier.md` | Onglet Build, editeur d'instructions |\n"
        + "".join(
            f"| `skills/{contenu_skill(f)[0]}/SKILL.md` | `{f}` | Onglet Build, panneau Composants, Skills |\n"
            for f in FICHES_SKILLS
        )
        + "\nPour modifier un contenu : editez la **fiche d'etape**, puis regenerez ce dossier avec\n"
        "`python3 outils/extraire-contenus-agent.py`. Un `git diff` vide apres regeneration\n"
        "prouve que le dossier est a jour.\n"
    )
    return fichiers


def main():
    verifier = "--verifier" in sys.argv
    ecarts = []
    for rel, contenu in attendus().items():
        cible = SORTIE / rel
        actuel = cible.read_text() if cible.exists() else None
        if actuel != contenu:
            ecarts.append(rel)
            if not verifier:
                cible.parent.mkdir(parents=True, exist_ok=True)
                cible.write_text(contenu)
    if verifier:
        if ecarts:
            print("DESYNCHRONISE : " + ", ".join(ecarts))
            return 1
        print("Contenus a jour.")
        return 0
    print(f"{len(attendus())} fichiers ecrits dans {SORTIE.relative_to(RACINE)}/"
          + (f" ({len(ecarts)} modifies)" if ecarts else " (aucun changement)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
