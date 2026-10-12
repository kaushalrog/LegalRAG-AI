# ⚖️ LegalRAG-AI

### Intelligent Legal Document Analysis using Sentence-BERT, FAISS, DCBD and LLaMA

LegalRAG-AI is a Retrieval-Augmented Generation (RAG) system for legal documents. You upload legal PDFs, ask a question, and the system retrieves the most relevant clauses and generates a report grounded only in those clauses. It then scores that report for faithfulness and hallucination risk using three independent methods.

The goal is to reduce irrelevant retrieval and unsupported LLM answers.

---

## 📌 Key Features

- **Multi-document upload**: analyze several legal PDFs at once
- **PDF extraction** with PyMuPDF (page count, character count, text preview)
- **Clause-level chunking** instead of fixed-size chunks
- **Sentence-BERT embeddings** for semantic understanding
- **FAISS index** built per document
- **Cross-document retrieval**: top results from every document are merged and ranked by similarity
- **Relevance validation**: rejects questions unrelated to the uploaded documents
- **DCBD (Dynamic Clause Boundary Detection)**: adaptively selects how many clauses to send to the LLM, instead of a fixed Top-k
- **LLaMA legal report** via Groq API, with a local transformers fallback
- **Fallback report** built directly from the retrieved clauses if no LLM is available
- **3-method hallucination detection**: Cosine Similarity, BERTScore, Jaccard Similarity
- **Interactive dark-themed Streamlit dashboard** with gauge charts, comparison bar chart and summary table
- **Downloadable report** (`.txt`) with the answer and all evaluation scores

---

## 🏗️ System Architecture

```
Legal PDF(s)
     ↓
PDF Text Extraction (PyMuPDF)
     ↓
Clause-Level Chunking
     ↓
Sentence-BERT Embeddings
     ↓
FAISS Index (one per document)
     ↓
User Question
     ↓
Semantic Retrieval (top 5 per document → merged → top 10)
     ↓
Relevance Validation
     ↓
DCBD Clause Selection
     ↓
LLaMA Legal Analysis Report
     ↓
Hallucination Detection (Cosine · BERTScore · Jaccard)
     ↓
Dashboard + Downloadable Report
```

---

## 🔬 Methodology

### 1. PDF Extraction
Text is extracted from each uploaded PDF with PyMuPDF. The app shows the number of pages, the character count and a preview.

### 2. Clause Chunking
The text is split into clauses, and each clause keeps its `clause_id` and source document name. Chunks are saved as JSON in `chunks/`.

### 3. Sentence-BERT Embeddings
Each clause is converted into a dense vector. Embeddings are saved in `embeddings/`.

### 4. FAISS Vector Store
A FAISS index and a metadata file are created for each document and stored in `faiss_index/`.

### 5. Semantic Retrieval
The question is embedded and searched against every document's index. The top 5 clauses per document are collected, merged, sorted by similarity score, and the top 10 are kept.

### 6. Relevance Validation
If the retrieved clauses are not similar enough to the question, the system stops and tells the user the question is unrelated to the uploaded documents. This prevents answers to off-topic questions.

### 7. DCBD Clause Selection
DCBD is an adaptive selection step. Instead of always using a fixed Top-k, it chooses the number of clauses from the similarity scores of the retrieved results. This keeps the LLM context focused on clauses that actually support the answer.

### 8. LLaMA Legal Analysis
Only the DCBD-selected clauses are sent to LLaMA, which generates the legal report. Two modes are supported:
- **Groq API** (set `GROQ_API_KEY`)
- **Local transformers fallback** (requires `transformers` and `torch`)

If neither is available, a fallback report is built directly from the retrieved clauses.

### 9. Faithfulness and Hallucination Evaluation
The generated report is compared against the selected clauses using three methods:

| Method | What it measures |
|---|---|
| **Cosine Similarity** | Embedding-level semantic match between answer and clauses |
| **BERTScore (F1)** | Token-level contextual similarity (precision, recall, F1) |
| **Jaccard Similarity** | Word-overlap between answer and clauses |

For each method, **Hallucination Risk = 100 − Faithfulness Score**. Higher faithfulness is better and lower hallucination risk is better. The dashboard shows the following:
- Gauge charts for each method (threshold marker at 70%)
- Exact score metrics
- A grouped bar chart comparing the methods
- A side-by-side summary table
- An overall answer-quality assessment

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit, Plotly |
| PDF Extraction | PyMuPDF |
| Embeddings | Sentence-Transformers (Sentence-BERT) |
| Vector Search | FAISS (CPU) |
| LLM | LLaMA via Groq API (local transformers fallback) |
| Evaluation | Cosine Similarity, BERTScore, Jaccard |
| Config | python-dotenv |
| Language | Python |

---

## 📂 Project Structure

```
LegalRAG-AI/
│
├── app.py                  # Streamlit application
├── requirements.txt
├── .gitignore
├── README.md
│
├── preprocessing/          # PDF extraction and clause chunking
├── models/                 # Sentence-BERT embedding generation
├── vectorstore/            # FAISS index management
├── retrieval/              # Retriever, relevance validator, DCBD
├── llm/                    # LLaMA manager (Groq / local)
├── evaluation/             # Faithfulness and hallucination evaluation
│
├── extracted_text/         # Extracted PDF text (generated)
├── chunks/                 # Clause chunks as JSON (generated)
├── embeddings/             # Saved embeddings (generated)
└── faiss_index/            # FAISS indexes and metadata (generated)
```

---

## ⚙️ Installation

```bash
git clone https://github.com/yakkalakarthikeya/LegalRAG-AI.git
cd LegalRAG-AI

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

**Requirements:** `streamlit`, `PyMuPDF`, `numpy`, `faiss-cpu`, `sentence-transformers`, `groq`, `python-dotenv`, `plotly`, `bert-score==0.3.13`

> For the local LLM fallback, also install: `pip install transformers torch`

---

## 🔑 Environment Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Never commit your `.env` file. Make sure it is listed in `.gitignore`.

---

## ▶️ How to Run

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal (usually `http://localhost:8501`).

---

## 🧭 How to Use

1. **Upload** one or more legal PDFs.
2. Click **🚀 Analyze Documents** to extract text, chunk clauses, generate embeddings and build the FAISS indexes.
3. Type your question under **💬 Ask a Legal Question** and click **🔍 Search**.
4. Review the **retrieved clauses** and the **DCBD-selected clauses**.
5. Read the generated **Legal Analysis Report**.
6. Check the **Hallucination Detection** dashboard.
7. Click **📥 Download Legal Report (.txt)** to save the result.

### Example

**Question:** *Can either party end the agreement before the contract expires?*

**Matching clause:** *"Either party may terminate this agreement prior to the expiration date..."*

Keyword search can miss this match because the wording differs. Semantic embeddings capture the meaning, so the clause is still retrieved.

---

## 💡 Why These Choices?

- **Sentence-BERT**: captures meaning, so differently worded questions still match the right clause
- **FAISS**: fast similarity search over dense vectors
- **Clause-level chunking**: keeps each legal clause intact and citable
- **DCBD**: adapts the number of clauses per question instead of a fixed Top-k
- **Three evaluation methods**: embedding, contextual and lexical views give a more reliable picture than any single metric

---

## ✅ Advantages

- Answers are grounded in the user's own documents
- Off-topic questions are rejected before generation
- Works across multiple documents
- Transparent: every retrieved and selected clause is shown with its score
- Quantified hallucination risk with three methods
- Still produces a clause-based report when no LLM is available

## ⚠️ Limitations

- Works only on text-based PDFs (scanned PDFs need OCR)
- Clause chunking quality depends on how well the document is structured
- Similarity-based evaluation is an estimate of faithfulness, not a guarantee
- LLM output quality depends on the model available (Groq or local)

## 🚀 Future Enhancements

- OCR support for scanned legal documents
- Cross-document clause comparison view
- Reference-answer based evaluation (RAGAS)
- Exportable PDF reports
- Cloud deployment

---

## 🔒 Security

- API keys are loaded from `.env` and are never hard-coded
- Uploaded documents are processed locally in the app environment

---

## 🧩 Troubleshooting

| Problem | Fix |
|---|---|
| "LLM initialization failed" | Add `GROQ_API_KEY` to `.env`, or install `transformers` and `torch` |
| First evaluation is slow | The BERTScore and embedding models load on first run |
| "Question is not related to the uploaded documents" | Ask a question based on the uploaded PDFs |
| Empty extraction | The PDF is probably scanned; use a text-based PDF |

---

## 🎓 Research Contribution

The main contribution is **DCBD**, an adaptive clause-selection method for legal RAG. It replaces fixed Top-k retrieval with a score-based selection, and it is paired with multi-method hallucination evaluation to measure how well answers stay grounded in the source clauses.

---

## ⚖️ Disclaimer

LegalRAG-AI is a research and educational project. Its output is **not legal advice**. Always consult a qualified legal professional and verify against the original documents.

---

## 👤 Author

**Y. Karthikeya**
B.Tech, Artificial Intelligence & Data Science
Amrita School of AI, Amrita Vishwa Vidyapeetham, Coimbatore
GitHub: [@yakkalakarthikeya](https://github.com/yakkalakarthikeya)
