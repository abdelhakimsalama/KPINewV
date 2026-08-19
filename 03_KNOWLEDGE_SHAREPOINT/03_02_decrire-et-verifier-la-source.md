# 03.02 — Décrire la source et vérifier qu'elle répond

## Objectif du fichier

- **À quoi sert ce fichier** : écrire la description de la source de Knowledge — qui n'est pas de la documentation mais le signal que l'orchestrateur lit pour décider d'interroger la liste — puis prouver que la source répond correctement.
- **Étape du développement** : étape 03, données. Elle suit immédiatement `03_01`.
- **Ce que vous faites dans Copilot Studio** : vous collez le nom et la description de la source, puis vous exécutez six tests de lecture.
- **Résultat attendu avant de passer à l'étape suivante** : les six tests rendent du contenu réel de la liste.

---

## Pourquoi la description compte

L'orchestrateur ne lit pas vos données pour décider s'il doit les consulter : il lit le **nom** et la **description** de la source. Une description vague produit deux défauts symétriques — la source n'est pas interrogée quand elle devrait l'être, ou elle l'est pour des questions hors sujet. Elle se rédige donc comme une consigne d'aiguillage : **de quoi ça parle, pour quelles questions, et pour lesquelles non**.

## Ce que vous faites

`Onglet Build > panneau Composants > Knowledge > KPIDictionary > modifier le nom et la description.`

**Nom de la source** — à copier tel quel :

```
KPIDictionary
```

> Gardez exactement ce nom. Les Instructions et les cinq Skills y font référence littéralement ; le renommer romprait ces références.

**Description de la source** — à copier telle quelle :

```
The official MyBI-to-SAC migration dictionary. The single source of truth for every KPI, field and dimension used in SAC reporting. Each row is one (SAC query, field) pair and carries: the Target Persona, the MyBI query name, the SAC query name, the official SAC field name in English and French, the former MyBI field name in English and French, the field type (Primary KPI, Derived KPI or Dimension), the calculation formula in English and French, and the business definition in English and French. Search this source for ANY question about what a KPI, field or dimension means, its formula, its type, which SAC query contains it, how a MyBI field was renamed in SAC, which fields are new in SAC, or which Target Persona a query belongs to. Do not use it for anything outside the MyBI-to-SAC reporting migration.
```

Enregistrez.

## Vérification : six lectures de contrôle

Onglet **Preview**. L'agent n'a pas encore ses règles définitives ; vous ne testez donc pas la mise en forme, seulement le fait que **la bonne information remonte**.

| # | Question à poser | Ce que vous devez voir remonter |
|---|---|---|
| 1 | `What does "Plant: Plant" mean?` | La définition officielle : un magasin reconnu comme division, pouvant aussi servir d'entrepôt |
| 2 | `Que signifie "Mat: Product category" ?` | Le secteur d'activité, avec ses exemples : alcool, parfum, soin |
| 3 | `Tell me about Stock Value` | Un contenu réel sur ce KPI, avec des noms de requêtes |
| 4 | `Quelle est la formule du taux de service aval Argon ?` | Une formule citée, du type « quantités préparées et livrées / quantité commandée » |
| 5 | `What is the field "Received (line)"?` | Le champ, et le fait que son équivalent MyBI est `New` |
| 6 | `Which queries are for the Supply persona?` | Des noms de requêtes SAC réels, associés à `Supply` |

**Comment lire les résultats à ce stade :** le contenu doit être **juste** et venir de la liste. La forme sera fausse — l'agent va sans doute produire des tableaux, compter, ou choisir un candidat. C'est normal : les règles arrivent à l'étape 04 et les procédures à l'étape 05. Ne corrigez rien ici.

**Un point mérite votre attention :** le test 5 doit faire apparaître la valeur `New`. À ce stade, l'agent la présentera probablement comme un nom de champ. C'est exactement le comportement que la règle 9 corrigera. Notez-le, ne le traitez pas.

## Diagnostic

| Symptôme | Interprétation | Correction |
|---|---|---|
| Un ou deux tests seulement échouent | Formulation de la question, ou champ mal indexé | Reformulez avec le libellé officiel exact ; si ça marche, ce n'est pas un défaut de source |
| Les six tests échouent | La source n'est pas interrogée ou ne rend rien | Vérifiez la recherche Dataverse, puis la description ci-dessus |
| L'agent répond de mémoire générale | La source n'est pas sélectionnée par l'orchestrateur | Recollez la description ; vérifiez qu'aucune autre source n'a été ajoutée |
| Les réponses citent une autre source | Une source parasite existe | Supprimez-la : la décision DA-03 impose une source unique |

## Ouvrez la trace d'activité au moins une fois

Pour l'un des six tests, ouvrez la **trace d'activité** de l'échange. Vous devez y voir la consultation de `KPIDictionary`. Prenez l'habitude dès maintenant : à partir de l'étape 05, cette trace sera le seul moyen de savoir **quel Skill s'est chargé** — et donc de diagnostiquer un comportement au lieu de le deviner depuis la réponse finale.

## Critères de fin d'étape

- [ ] Le nom de la source est exactement `KPIDictionary`.
- [ ] La description est collée et enregistrée.
- [ ] Les six lectures de contrôle rendent du contenu réel de la liste.
- [ ] J'ai ouvert la trace d'activité au moins une fois et j'y ai vu la consultation de la source.
- [ ] Je passe au dossier `04_INSTRUCTIONS`.
