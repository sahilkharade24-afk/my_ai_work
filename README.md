Retrieval-Augmented Generation (RAG) is an AI framework that improves the accuracy and relevance of large language model (LLM) outputs by fetching, or "retrieving," trusted, up-to-date information from external data sources before generating a response. It reduces hallucinations and provides grounded, context-aware answers without needing to retrain the underlying model. 
How RAG Works
RAG operates by enhancing LLMs with external knowledge, typically following this process:
Retrieve: When a user poses a query, the system searches authorized internal documents, databases, or the web to find relevant information.
Augment: The user's prompt is combined with the retrieved, relevant data to create an enhanced prompt.
Generate: The LLM uses this specific context to generate an accurate, informed response. 

During this project, I designed and implemented multiple Retrieval-Augmented Generation (RAG)
architectures to improve the accuracy, reliability, and reasoning capability of AI-based questionanswering systems. My work focused on building, testing, and comparing different retrieval strategies
and system designs, starting from basic RAG pipelines and progressing toward advanced, agent-driven
architectures. The goal was to understand how different retrieval mechanisms impact answer quality
and to create scalable, modular RAG systems suitable for real-world applications.

I first implemented the Naive RAG model, which serves as the baseline architecture. In this approach,
documents are processed, chunked, embedded, and stored in a vector database. When a user query is
received, the system retrieves the most similar text chunks using vector similarity and passes them
directly to the language model for answer generation. This model helped establish the core RAG
pipeline and provided a benchmark for evaluating more advanced approaches.


