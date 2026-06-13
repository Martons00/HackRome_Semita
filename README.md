# SemitaAI CareerPathEngine

Questo progetto definisce una chain LangChain per generare percorsi di carriera realistici e strutturati a partire da un profilo utente validato.

## Setup locale su Mac M1 16GB

```bash
pip install -r requirements.txt
```

Il modello di default e' `Qwen/Qwen2.5-1.5B-Instruct`, abbastanza piccolo per girare localmente su Mac M1 16GB tramite PyTorch/MPS.

## Uso rapido

```bash
python examples/run_local_hf_career_path_engine.py
```

Per provare un modello un po' piu' forte, ma piu' lento:

```bash
HF_MODEL_ID="Qwen/Qwen2.5-3B-Instruct" python examples/run_local_hf_career_path_engine.py
```

Il motore restituisce sempre un oggetto `CareerPathOutput` validato con Pydantic, pronto per essere letto da una UI.

## Struttura

- `career_path_engine/schemas.py`: modelli `UserProfile` e `CareerPathOutput`.
- `career_path_engine/prompts.py`: prompt principale e istruzioni operative dell'agente.
- `career_path_engine/local_hf.py`: engine locale Hugging Face con parsing e validazione JSON.
- `career_path_engine/chain.py`: factory opzionale per usare una chain LangChain con modelli compatibili.
- `examples/run_local_hf_career_path_engine.py`: esempio basato sul notebook iniziale.

## Note pratiche

Alla prima esecuzione Hugging Face scarica il modello. Dopo il download, il modello rimane nella cache locale.

Se il JSON non e' valido, l'engine fallisce esplicitamente invece di restituire dati mezzi rotti: meglio accorgersene subito quando si integra una UI.
