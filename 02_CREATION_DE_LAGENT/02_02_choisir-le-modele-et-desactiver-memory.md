# 02.02 — Choisir le modèle et désactiver Memory

## Objectif du fichier

- **À quoi sert ce fichier** : fixer les deux réglages du panneau de composants qui influencent le comportement de l'agent avant même qu'il ait des règles.
- **Étape du développement** : étape 02, création.
- **Ce que vous faites dans Copilot Studio** : vous sélectionnez le modèle et vous vérifiez que Memory est désactivée.
- **Résultat attendu avant de passer à l'étape suivante** : un modèle OpenAI/Microsoft est sélectionné, Memory est sur OFF, et ces choix sont notés.

---

## 1. Le modèle

**Où** : `Onglet Build > panneau Composants (à droite) > Model`.

**Ce que vous choisissez** : un modèle **OpenAI / Microsoft**. Les modèles Anthropic sont exclus de ce projet **[CHOIX PROJET]** — motif : ils exigent une activation du locataire et leur traitement s'effectue hors des environnements gérés par Microsoft.

**Lequel** : le catalogue évolue vite et dépend de votre locataire **[À VÉRIFIER]**. La règle de choix, elle, ne change pas :

| Privilégiez | Évitez |
|---|---|
| Un modèle **conversationnel GA** de la génération courante | Un modèle marqué **expérimental** ou **préversion** |
| Un modèle rapide : l'agent fait de la recherche documentaire, pas du raisonnement profond | Un modèle de raisonnement profond : latence et coût supérieurs, sans bénéfice ici |

> **N'attribuez pas ce choix au hasard, mais ne le sacralisez pas non plus.** Le modèle est un paramètre, pas une architecture : vous pourrez le changer à l'étape 06 si l'évaluation montre un écart. Notez simplement lequel vous avez retenu, parce qu'un changement de modèle est un **déclencheur de non-régression** (voir `06_03`).

**Notez ici votre choix :**

```
Modèle retenu :
Date :
Motif :
```

## 2. Memory : OFF

**Où** : `Onglet Build > panneau Composants > Memory`.

**Ce que vous faites** : vérifiez que Memory est **désactivée**. C'est normalement l'état par défaut ; ne l'activez pas.

**Pourquoi** (décision DA-06) : Memory retient des préférences et des habitudes par utilisateur d'une conversation à l'autre. Or ce projet interdit d'inférer un persona et de filtrer sur une hypothèse. Un agent qui « se souviendrait » qu'un utilisateur travaille au Supply pourrait orienter silencieusement ses réponses suivantes — exactement le comportement que la règle 6 proscrit. La fonctionnalité est de surcroît en préversion **[OFFICIEL]**.

**Si vous voulez malgré tout l'évaluer un jour** : ce n'est pas un débat d'opinion, c'est une mesure. Passez la suite de tests de l'étape 06 avec Memory OFF, puis ON, et comparez. Tant que la mesure n'est pas faite, la réponse reste OFF.

## 3. Les composants que vous laissez vides

Pendant que vous êtes dans le panneau, prenez acte de ce qui restera vide **définitivement** dans cette architecture :

| Composant | État cible | Motif |
|---|---|---|
| **Tools** | Vide | L'agent lit, il n'agit sur aucun système externe |
| **Connected agents** | Vide | Un seul domaine, un seul propriétaire |
| **Microsoft IQ** | Non configuré | Introduirait du contexte non autoritaire |
| **Knowledge** | 1 source, à l'étape 03 | La liste `KPIDictionary`, et rien d'autre |
| **Skills** | 5, à l'étape 05 | Les cinq comportements métier |

Si, au fil du projet, l'un de ces « vide » devient tentant à remplir, retournez d'abord à `01_02` : la décision et son motif y sont écrits.

## Vérification

1. Onglet **Preview**, posez une question quelconque.
2. Ouvrez la **trace d'activité** de l'échange.
3. Vous devez y voir le modèle sollicité, et **aucun** chargement de Skill ni de source (il n'y en a pas encore).

## Critères de fin d'étape

- [ ] Un modèle OpenAI/Microsoft GA est sélectionné, et son nom est noté ci-dessus.
- [ ] Memory est sur OFF.
- [ ] Tools, Connected agents et Microsoft IQ sont vides.
- [ ] Je passe au dossier `03_KNOWLEDGE_SHAREPOINT`.
