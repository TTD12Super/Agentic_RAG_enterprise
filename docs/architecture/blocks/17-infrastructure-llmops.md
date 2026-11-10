# 17 — Infrastructure & LLMOps

## Trách nhiệm
containers, CI/CD, secrets, backups, migrations, rollback.

## Đầu vào
Source, configs, secrets manager and deploy instructions.

## Đầu ra / contract
Reproducible secure runtime and monitoring.

## ARCH-OVERVIEW alignment

- Operate the Python/FastAPI Core MVP, Python RAG workers, Python ingestion workers, queue, authoritative data stores, external model gateway and observability. Rust is a benchmark candidate.
- Cloud topology, broker, database, search engine, cache/checkpoint store and Rust framework remain proposed until approved ADRs exist.
- Capacity work must define the 500-user workload, worker concurrency, provider limits, queue wait and processing latency before claiming support.
- Keep private networks, least-privileged identities, managed secrets, backup/restore and rollback evidence.

## Ranh giới bảo mật
Private DB network, least-privileged secrets, no prod deploy by agent.

## Kiểm thử bàn giao
Static checks, recovery restore, migrations and health checks.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- PostgreSQL 17 is authoritative and owns the durable queue/checkpoint; Qdrant is rebuildable from source data; object storage is private and versioned; Redis is non-authoritative.
- Alembic is the single migration owner for the Python/FastAPI MVP.
- Dev, staging and production use separate secrets, databases and buckets. Provider/cloud/region remain pending.
- PostgreSQL uses daily base backup plus continuous WAL/PITR; proposed RPO ≤1 hour and RTO ≤4 hours require quarterly restore evidence.
- Peak verification targets 500 active sessions, 30 queries/minute sustained and 60 queries/minute for a five-minute burst.

## Student/demo deployment profiles

- Managed profile: Vercel frontend, Azure for Students container services, Qdrant Cloud Free and development-tier storage.
- Self-managed profile: Vercel frontend plus an Oracle Always Free VM running API, RAG worker, ingestion worker and development data containers.
- Both profiles are for learning/demo only. They do not provide evidence for 500-session capacity, production RPO/RTO, multi-AZ availability or enterprise data compliance.
- External LLM provider billing and data-processing terms are separate from student cloud credits.
