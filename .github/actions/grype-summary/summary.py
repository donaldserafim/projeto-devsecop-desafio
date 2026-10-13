import json
import os
from pathlib import Path


def cell(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace("|", "&#124;")
            .replace("\r", " ").replace("\n", " "))


outcome = os.environ.get("GRYPE_OUTCOME", "skipped")
report = Path(os.environ.get("GRYPE_REPORT", "grype.json"))
data = None
try:
    candidate = json.loads(report.read_text())
    if isinstance(candidate, dict) and isinstance(candidate.get("matches"), list):
        data = candidate
except (OSError, ValueError):
    pass

matches = data["matches"] if data is not None else []
severity_order = {"critical": 5, "high": 4, "medium": 3, "low": 2, "negligible": 1}
blocking = [match for match in matches
            if severity_order.get(match.get("vulnerability", {}).get("severity", "").lower(), 0) >= 3]
summary = ["## 📦 Resultado do Grype — Dependências", ""]
if outcome == "skipped":
    summary += ["### ⚪ GRYPE NÃO EXECUTADO", "",
                "> A análise não foi executada. Confira as etapas anteriores."]
elif outcome != "success":
    summary += ["### 🚫 PIPELINE BLOQUEADA NA ETAPA GRYPE", "",
                "> **O job de build falhou nesta etapa. O deploy não será executado.**", ""]
    if blocking:
        summary += [f"**Motivo:** {len(blocking)} ocorrência(s) com severidade Medium, High ou Critical.",
                    "Atualize as dependências afetadas e execute a pipeline novamente."]
    else:
        summary += ["**Motivo:** falha na execução da análise. Consulte os logs da etapa **Executar o grype**."]
elif data is None or blocking:
    summary += ["### ⚠️ RESULTADO REQUER VERIFICAÇÃO", "",
                "> O relatório está ausente, inválido ou diverge do limite de bloqueio. Consulte os logs do Grype."]
else:
    summary += ["### ✅ APROVADO PELO GRYPE", "",
                "> Nenhuma ocorrência atingiu o limite de bloqueio. Esta etapa permite que a pipeline continue."]

summary += ["", "**Limite de bloqueio:** Medium ou superior (`--fail-on medium`).", ""]
if data is not None:
    summary += [f"**Ocorrências encontradas:** {len(matches)} · **No limite de bloqueio:** {len(blocking)}", ""]
    if matches:
        counts = {}
        for match in matches:
            severity = match.get("vulnerability", {}).get("severity", "Unknown")
            counts[severity] = counts.get(severity, 0) + 1
        summary += [" · ".join(f"**{cell(severity)}:** {count}" for severity, count in
                              sorted(counts.items(), key=lambda item: -severity_order.get(item[0].lower(), 0))), "",
                    "| Severidade | Dependência | Versão instalada | Vulnerabilidade | Versões com correção |",
                    "|---|---|---|---|---|"]
        for match in sorted(matches, key=lambda match: -severity_order.get(
                match.get("vulnerability", {}).get("severity", "").lower(), 0)):
            vulnerability = match.get("vulnerability", {})
            artifact = match.get("artifact", {})
            severity = vulnerability.get("severity", "Unknown")
            icon = {"critical": "🔴", "high": "🔴", "medium": "🟠", "low": "🟡"}.get(severity.lower(), "⚪")
            versions = vulnerability.get("fix", {}).get("versions", [])
            fixed = ", ".join(versions) if versions else "Não informadas"
            summary.append(f"| {icon} {cell(severity)} | {cell(artifact.get('name', '?'))} | "
                           f"{cell(artifact.get('version', '?'))} | {cell(vulnerability.get('id', '?'))} | {cell(fixed)} |")
else:
    if outcome != "skipped":
        summary += ["⚠️ O relatório JSON está ausente ou inválido; isso não significa ausência de vulnerabilidades."]

with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
    output.write("\n".join(summary) + "\n")
