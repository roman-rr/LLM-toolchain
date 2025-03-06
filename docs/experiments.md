# Experiments

This document tracks the various experiments conducted within the LangChain project, recording key details, objectives, methodology, and outcomes for future reference and reproducibility.

## DEMO 🔬 Experiment 001: Evaluating RAG Embedding Models

**Date:** 2025-03-06  
**Researcher:** Roman Antonov

### Objective
Determine which embedding model (OpenAI Ada, Cohere, Sentence Transformers) yields the best retrieval quality for PDF-based RAG tasks.

### Methodology
- Selected 50 diverse PDF documents.
- Embedded documents using:
  - OpenAI Ada Embeddings
  - Cohere multilingual embeddings
  - Sentence Transformers (all-MiniLM)
- Evaluated with a set of 20 predefined questions.
- Measured accuracy and response quality using human reviewers (5 reviewers).

### Results
| Model                | Accuracy (%) | Avg. Retrieval Time (s) |
|----------------------|--------------|-------------------------|
| OpenAI Ada           | 87.2         | 0.52                    |
| Cohere multilingual  | 85.5         | 0.48                    |
| Sentence Transformers| **91.6**     | 0.65                    |

### Conclusion
Sentence Transformers (multilingual) provided the best accuracy for our use-case. Slightly slower but still within acceptable limits.

### Action Items
- Adopt Sentence Transformers for embeddings.
- Further optimize performance for real-time retrieval.

---

## Next Experiments
- [ ] One
- [ ] ???
- [ ] ???
- [ ] ???
- [ ] Profit
