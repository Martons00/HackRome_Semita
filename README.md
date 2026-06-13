# SemitaAI CareerPathEngine

Questo progetto definisce una chain LangChain per generare percorsi di carriera realistici e strutturati a partire da un profilo utente validato.

## Setup locale su Mac M1 16GB

```bash
pip install -r requirements.txt
```

Se lavori da Colab o da una cartella diversa dalla root del repo, installa anche il package in modalita' editabile:

```bash
pip install -e .
```

Il modello di default e' `Qwen/Qwen2.5-1.5B-Instruct`, abbastanza piccolo per girare localmente su Mac M1 16GB tramite PyTorch/MPS.

## Uso rapido

```bash
python examples/run_local_hf_career_path_engine.py
```

L'esempio usa le ESCO REST API per cercare occupazioni e skill correlate al ruolo target, poi passa quel contesto al modello locale Hugging Face.

## Demo Google Colab

Puoi usare il notebook `SemitaTestCareerEngine.ipynb` come demo caricandolo manualmente su Google Colab.

In alternativa, puoi aprire direttamente questa demo gia' caricata:

[Apri la demo su Google Colab](https://colab.research.google.com/drive/1t9a4gy8UPhOLFM9CoRpOT12dxsjsVoUo?usp=sharing)

Per provare un modello un po' piu' forte, ma piu' lento:

```bash
HF_MODEL_ID="Qwen/Qwen2.5-3B-Instruct" python examples/run_local_hf_career_path_engine.py
```

Il motore restituisce sempre un oggetto `CareerPathOutput` validato con Pydantic, pronto per essere letto da una UI.

## Struttura

- `career_path_engine/schemas.py`: modelli `UserProfile` e `CareerPathOutput`.
- `career_path_engine/prompts.py`: prompt principale e istruzioni operative dell'agente.
- `career_path_engine/esco.py`: client ESCO REST API e retriever per definizione dei ruoli/skill.
- `career_path_engine/local_hf.py`: engine locale Hugging Face con parsing e validazione JSON.
- `career_path_engine/chain.py`: factory opzionale per usare una chain LangChain con modelli compatibili.
- `examples/run_local_hf_career_path_engine.py`: esempio basato sul notebook iniziale.

## ESCO REST API

Il retriever chiama:

- `/search` con `type=occupation` per derivare ruoli simili al target.
- `/search` con `type=skill` per trovare skill correlate.
- `/resource/occupation?uri=...` per recuperare il dettaglio del ruolo.
- `/resource/skill?uri=...` per recuperare il dettaglio della skill.

La lingua di default e' inglese. Puoi cambiarla cosi':

```bash
ESCO_LANGUAGE=it python examples/run_local_hf_career_path_engine.py
```

## Note pratiche

Alla prima esecuzione Hugging Face scarica il modello. Dopo il download, il modello rimane nella cache locale.

Se il JSON non e' valido, l'engine fallisce esplicitamente invece di restituire dati mezzi rotti: meglio accorgersene subito quando si integra una UI.
