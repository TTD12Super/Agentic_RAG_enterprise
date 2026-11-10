"""Provider-neutral security guardrails for untrusted agent data.

These checks are defense-in-depth. They never authenticate a principal, grant
authorization, or replace the policy checks at retrieval, tool, and citation
boundaries.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
import unicodedata


MAX_INPUT_CHARS = 8_000
MAX_CONTEXT_CHARS = 12_000
MAX_OUTPUT_CHARS = 16_000
MAX_CITATION_CHARS = 4_000

ALLOWED_TOOL_ACTIONS: Mapping[str, frozenset[str]] = {
    "search_documents": frozenset({"search", "tool:execute"}),
    "read_authorized_chunk": frozenset({"read", "tool:execute"}),
    "get_document_metadata": frozenset({"metadata", "read", "tool:execute"}),
}


@dataclass(frozen=True)
class GuardrailResult:
    """A safe value is returned only when ``allowed`` is true."""

    allowed: bool
    value: str | None
    reason_codes: tuple[str, ...] = ()
    redacted: bool = False


@dataclass(frozen=True)
class ToolDecision:
    """Allowlist result; an allowed result is not an authorization decision."""

    allowed: bool
    tool: str | None
    action: str | None
    reason_codes: tuple[str, ...] = ()
    requires_authorization: bool = True
    authorization_granted: bool = False


@dataclass(frozen=True)
class Citation:
    """The minimum provenance needed for the lexical grounding gate."""

    source_id: str
    excerpt: str


@dataclass(frozen=True)
class RedactionResult:
    text: str
    categories: tuple[str, ...] = ()

    @property
    def changed(self) -> bool:
        return bool(self.categories)


_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "instruction_override",
        re.compile(
            r"\b(?:(?:ignore|disregard|forget|override|bypass)|do\s+not\s+follow)\b"
            r".{0,100}\b(?:previous|prior|earlier|above|system|developer|safety|security)"
            r"\s+(?:instructions?|rules?|policy|message)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "prompt_or_secret_exfiltration",
        re.compile(
            r"\b(?:reveal|show|print|dump|leak|disclose|repeat)\b"
            r".{0,100}\b(?:system prompt|system instructions?|developer message|hidden instructions?|"
            r"secrets?|api keys?|access tokens?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "privilege_impersonation",
        re.compile(
            r"\b(?:you are now|act as|pretend to be|impersonate)\b"
            r".{0,50}\b(?:admin|administrator|system|developer|root)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "safety_or_authorization_bypass",
        re.compile(
            r"\b(?:disable|turn off|remove|bypass)\b"
            r".{0,80}\b(?:guardrails?|safety|filters?|authorization|"
            r"permission checks?|access controls?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "instruction_replacement",
        re.compile(
            r"\b(?:follow|obey)\s+(?:only|these|the following)\b"
            r".{0,60}\b(?:instructions?|commands?|rules?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "vietnamese_instruction_override",
        re.compile(
            r"\b(?:bỏ qua|bo qua|phớt lờ|phot lo|ghi đè|ghi de)\b"
            r".{0,100}\b(?:hướng dẫn|huong dan|chỉ dẫn|chi dan|quy tắc|quy tac|"
            r"hệ thống|he thong|phân quyền|phan quyen)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "vietnamese_exfiltration_or_impersonation",
        re.compile(
            r"\b(?:tiết lộ|tiet lo|hiển thị|hien thi|giả làm|gia lam|đóng vai|dong vai)\b"
            r".{0,80}\b(?:prompt|hướng dẫn|huong dan|quản trị|quan tri|admin|bí mật|bi mat)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
)

_EDUCATIONAL_CONTEXT = re.compile(
    r"\b(?:what does|what is|explain|example|detect|defend|mitigate|prevent|"
    r"analy[sz]e|test|how can|how do)\b.{0,100}\b(?:prompt injection|jailbreak|"
    r"system prompt|security)\b",
    re.IGNORECASE | re.DOTALL,
)
_DIRECT_COMMAND = re.compile(
    r"^\s*(?:ignore|disregard|forget|reveal|show|dump|pretend|impersonate|"
    r"disable|bypass|follow|obey)\b",
    re.IGNORECASE,
)

_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "private_key",
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.IGNORECASE | re.DOTALL,
        ),
        "[REDACTED_SECRET]",
    ),
    (
        "jwt",
        re.compile(
            r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\."
            r"[A-Za-z0-9_-]{8,}(?![A-Za-z0-9_-])",
        ),
        "[REDACTED_SECRET]",
    ),
    (
        "api_key",
        re.compile(
            r"(?<![A-Za-z0-9_-])(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9_]{20,}|"
            r"github_pat_[A-Za-z0-9_]{20,})(?![A-Za-z0-9_-])",
        ),
        "[REDACTED_SECRET]",
    ),
    (
        "secret_assignment",
        re.compile(
            r"\b(?:api[_ -]?key|access[_ -]?token|auth[_ -]?token|password|passwd|"
            r"secret|client[_ -]?secret)\b\s*[:=]\s*"
            r"(?:[\"'][^\"'\r\n]{1,}[\"']|[^\s,;}]{1,})",
            re.IGNORECASE,
        ),
        "[REDACTED_SECRET]",
    ),
    (
        "email",
        re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?![\w.-])"),
        "[REDACTED_EMAIL]",
    ),
    (
        "phone",
        re.compile(r"(?<!\w)(?:\+?84[ -]?(?:3|5|7|8|9)\d{8}|0(?:3|5|7|8|9)\d{8})(?!\w)"),
        "[REDACTED_PHONE]",
    ),
    (
        "ssn",
        re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
        "[REDACTED_PII]",
    ),
)
_CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")

_SENSITIVE_TERMS = frozenset(
    {
        "salary",
        "salaries",
        "payroll",
        "compensation",
        "password",
        "secret",
        "secrets",
        "token",
        "tokens",
        "api",
        "ssn",
        "phone",
        "email",
        "address",
        "bank",
        "medical",
        "health",
        "financial",
        "revenue",
        "profit",
        "confidential",
        "restricted",
        "private",
        "personal",
    }
)
_STOP_WORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "from",
        "into",
        "about",
        "what",
        "when",
        "where",
        "which",
        "will",
        "have",
        "has",
        "are",
        "was",
        "were",
        "is",
        "a",
        "an",
        "to",
        "of",
        "in",
        "on",
        "or",
        "as",
        "be",
        "by",
        "của",
        "và",
        "là",
        "cho",
        "trong",
    }
)


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("\r\n", "\n").replace("\r", "\n")
    clean: list[str] = []
    for char in value:
        category = unicodedata.category(char)
        if char in "\n\t" or category not in {"Cc", "Cf"}:
            clean.append(char)
        elif category == "Cf":
            continue
        else:
            clean.append(" ")
    value = "".join(clean)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _luhn_valid(value: str) -> bool:
    digits = [int(char) for char in value if char.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def redact_sensitive_data(value: str) -> RedactionResult:
    """Redact high-confidence secrets and common direct PII without logging input."""

    if not isinstance(value, str):
        raise TypeError("sensitive-data redaction requires text")

    text = value
    categories: set[str] = set()
    for category, pattern, replacement in _SECRET_PATTERNS:
        if pattern.search(text):
            categories.add(category)
            text = pattern.sub(replacement, text)

    def redact_card(match: re.Match[str]) -> str:
        if _luhn_valid(match.group(0)):
            categories.add("credit_card")
            return "[REDACTED_PAYMENT]"
        return match.group(0)

    text = _CARD_PATTERN.sub(redact_card, text)
    return RedactionResult(text=text, categories=tuple(sorted(categories)))


def detect_prompt_injection(value: str) -> tuple[str, ...]:
    """Return high-confidence injection categories; this is intentionally heuristic."""

    if not isinstance(value, str):
        return ("invalid_input",)
    text = _normalize_text(value)
    matches = tuple(code for code, pattern in _INJECTION_PATTERNS if pattern.search(text))
    if _EDUCATIONAL_CONTEXT.search(text) and not _DIRECT_COMMAND.search(text) and not matches:
        return ()
    return matches


def _inspect_text(value: object, *, max_chars: int, injection_prefix: str) -> GuardrailResult:
    if not isinstance(value, str):
        return GuardrailResult(False, None, ("invalid_input_type",))
    normalized = _normalize_text(value)
    if not normalized:
        return GuardrailResult(False, None, ("empty_input",))
    if len(normalized) > max_chars:
        return GuardrailResult(False, None, ("input_too_large",))
    injection_codes = detect_prompt_injection(normalized)
    if injection_codes:
        return GuardrailResult(
            False,
            None,
            tuple(f"{injection_prefix}_{code}" for code in injection_codes),
        )
    redacted = redact_sensitive_data(normalized)
    return GuardrailResult(True, redacted.text, redacted.categories, redacted=redacted.changed)


def normalize_user_input(value: object, *, max_chars: int = MAX_INPUT_CHARS) -> GuardrailResult:
    """Normalize, bound, inspect, and redact a user message."""

    return _inspect_text(value, max_chars=max_chars, injection_prefix="direct_prompt_injection")


def inspect_untrusted_content(value: object, *, max_chars: int = MAX_CONTEXT_CHARS) -> GuardrailResult:
    """Inspect retrieved/document/tool content as data, never as instructions."""

    return _inspect_text(value, max_chars=max_chars, injection_prefix="indirect_prompt_injection")


_UNTRUSTED_AUTH_ARGUMENTS = frozenset(
    {
        "allowed_document_ids",
        "is_admin",
        "principal",
        "principal_id",
        "role",
        "roles",
        "tenant_id",
    }
)


def validate_tool_request(
    tool: object,
    *,
    action: object | None = None,
    arguments: object | None = None,
) -> ToolDecision:
    """Allow only the read-only MVP tool set; never grant the tool permission."""

    if not isinstance(tool, str) or tool not in ALLOWED_TOOL_ACTIONS:
        return ToolDecision(False, tool if isinstance(tool, str) else None, None, ("tool_not_allowed",))
    if arguments is not None and not isinstance(arguments, Mapping):
        return ToolDecision(False, tool, None, ("invalid_tool_arguments",))
    if isinstance(arguments, Mapping):
        supplied = {
            str(key).strip().casefold().replace("-", "_")
            for key in arguments
        }
        if supplied & _UNTRUSTED_AUTH_ARGUMENTS:
            return ToolDecision(False, tool, None, ("untrusted_authorization_argument",))

    normalized_action = "tool:execute" if action is None else action
    if not isinstance(normalized_action, str):
        return ToolDecision(False, tool, None, ("invalid_tool_action",))
    normalized_action = normalized_action.strip().casefold()
    if normalized_action not in ALLOWED_TOOL_ACTIONS[tool]:
        return ToolDecision(False, tool, normalized_action, ("tool_action_not_allowed",))
    return ToolDecision(
        True,
        tool,
        normalized_action,
        requires_authorization=True,
        authorization_granted=False,
    )


_TOKEN_PATTERN = re.compile(r"\b[\w'-]{3,}\b", re.UNICODE)
_ABSTENTION_PATTERN = re.compile(
    r"^\s*(?:i\s+(?:cannot|can't|can’t|am unable)|unable to|"
    r"no relevant information|not enough evidence|"
    r"không thể|không tìm thấy|chưa đủ thông tin)\b",
    re.IGNORECASE,
)


def _terms(value: str) -> set[str]:
    return {
        term.casefold()
        for term in _TOKEN_PATTERN.findall(value)
        if term.casefold() not in _STOP_WORDS
    }


def _sensitive_terms(value: str) -> set[str]:
    terms = _terms(value)
    return terms & _SENSITIVE_TERMS


def _citation(item: object) -> Citation | None:
    if isinstance(item, Citation):
        candidate = item
    elif isinstance(item, Mapping):
        source_id = item.get("source_id", item.get("document_id", item.get("id")))
        excerpt = item.get("excerpt", item.get("quote", item.get("text")))
        if item.get("authorized") is False:
            return None
        if not isinstance(source_id, str) or not isinstance(excerpt, str):
            return None
        candidate = Citation(source_id, excerpt)
    else:
        return None
    if not candidate.source_id.strip() or not candidate.excerpt.strip():
        return None
    if len(candidate.source_id) > 256 or len(candidate.excerpt) > MAX_CITATION_CHARS:
        return None
    return Citation(_normalize_text(candidate.source_id), _normalize_text(candidate.excerpt))


def validate_output(value: object, citations: Sequence[object] | None = None) -> GuardrailResult:
    """Require citation-backed output and redact high-confidence leakage.

    Grounding is a conservative lexical gate, not semantic entailment. The
    caller must supply citations that were already authorized by the backend.
    """

    if not isinstance(value, str):
        return GuardrailResult(False, None, ("invalid_output_type",))
    normalized = _normalize_text(value)
    if not normalized:
        return GuardrailResult(False, None, ("empty_output",))
    if len(normalized) > MAX_OUTPUT_CHARS:
        return GuardrailResult(False, None, ("output_too_large",))

    redacted = redact_sensitive_data(normalized)
    if detect_prompt_injection(redacted.text):
        return GuardrailResult(False, None, ("output_prompt_injection",))

    if _ABSTENTION_PATTERN.search(redacted.text):
        return GuardrailResult(True, redacted.text, redacted.categories, redacted=redacted.changed)
    if citations is None or isinstance(citations, (str, bytes)):
        return GuardrailResult(False, None, ("missing_citations",))
    if not citations:
        return GuardrailResult(False, None, ("missing_citations",))

    parsed = tuple(_citation(item) for item in citations)
    if not parsed or any(item is None for item in parsed):
        return GuardrailResult(False, None, ("invalid_citation",))
    evidence = " ".join(item.excerpt for item in parsed if item is not None)
    output_terms = _terms(redacted.text)
    evidence_terms = _terms(evidence)
    sensitive_terms = _sensitive_terms(redacted.text)
    if sensitive_terms - evidence_terms:
        return GuardrailResult(False, None, ("unsupported_sensitive_claim",))
    if not output_terms & evidence_terms:
        return GuardrailResult(False, None, ("unsupported_claim",))
    return GuardrailResult(True, redacted.text, redacted.categories, redacted=redacted.changed)

