flowchart LR
  U["User CLI<br/>Topic, Age, Style, Moral"]
  O["StorytellingApp<br/>(Orchestrator)"]
  S["Storyteller<br/>(gpt-3.5-turbo)"]
  J["Judge<br/>(gpt-3.5-turbo, temp=0.0)"]
  R["Reviser<br/>(gpt-3.5-turbo)"]
  F["Final Story + Scores"]

  %% High-level flow
  U --> O
  O --> S
  S -- "Draft story" --> J
  J -- "JSON: scores, overall, feedback" --> O

  %% Decision & loop
  O -- "overall ≥ threshold" --> F
  O -- "overall < threshold & loops < max" --> R
  R -- "Targeted edits" --> S

  %% Optional: show the single API these roles call
  subgraph API["OpenAI ChatCompletion API"]
    ChatAPI["ChatCompletion"]
  end
  
  S -. calls .-> ChatAPI
  J -. calls .-> ChatAPI
  R -. calls .-> ChatAPI
