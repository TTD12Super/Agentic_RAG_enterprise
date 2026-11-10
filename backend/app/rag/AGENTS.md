# RAG scoped instructions

Read `docs/contracts/retrieval.md` and `docs/rag/retrieval-design.md`. Always filter authorized tenant, approved ACTIVE version and ACL in **both** dense and BM25 queries. Recheck before returning context; parent expansion and citation fetch require new authorization checks. Benchmark baseline + RRF + rerank on evaluation fixtures. Do not use retrieval scores as probability of correctness.
