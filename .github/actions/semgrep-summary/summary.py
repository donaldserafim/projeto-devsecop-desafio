import json
import os
from pathlib import Path

outcome = os.environ.get("SEMGREP_OUTCOME", "skipped")
report = Path(os.environ.get("SEMGREP_REPORT", "semgrep.json"))
data = None
try:
    data = json.loads(report.read_text())
except (OSError, ValueError):
    pass

findings = data.get("results", []) if data else []
errors = data.get("errors", []) if data else []
summary = ["## 🔍 Resultado do Semgrep", ""]
if outcome == "skipped":
    summary += ["### ⚪ SEMGREP NÃO EXECUTADO", "",
                "> A análise não foi executada. Confira as etapas anteriores."]
elif outcome != "success":
    summary += ["### 🚫 PIPELINE BLOQUEADA NA ETAPA SEMGREP", "",
                "> **O job de build falhou nesta etapa. O deploy não será executado.**", ""]
    if findings:
        summary += [f"**Motivo:** {len(findings)} problema(s) encontrado(s). Corrija os itens abaixo e execute a pipeline novamente."]
    else:
        summary += ["**Motivo:** falha na execução da análise. Consulte os logs da etapa **SAST - Semgrep**."]
elif data is None or findings or errors:
    summary += ["### ⚠️ RESULTADO REQUER VERIFICAÇÃO", "",
                "> O resultado não confirma uma análise sem problemas. Consulte os logs do Semgrep."]
else:
    summary += ["### ✅ APROVADO PELO SEMGREP", "",
                "> Nenhum problema encontrado."]

def cell(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("\r", " ").replace("\n", " ")

if data is not None:
    summary += ["", f"**Problemas encontrados:** {len(findings)} · **Erros de análise:** {len(errors)}", ""]
if findings:
    summary += ["| Severidade | Local | Problema | Regra |", "|---|---|---|---|"]
    for finding in findings:
        extra = finding.get("extra", {})
        severity = extra.get("severity", "UNKNOWN")
        icon = {"ERROR": "🔴", "WARNING": "🟠", "INFO": "🔵"}.get(severity, "⚪")
        location = f"{finding.get('path', '?')}:{finding.get('start', {}).get('line', '?')}"
        summary.append(f"| {icon} {cell(severity)} | {cell(location)} | {cell(extra.get('message', ''))} | {cell(finding.get('check_id', ''))} |")
if errors:
    summary += ["", "**Erros informados pelo scanner:**", ""]
    summary += ["- " + cell(error.get("message", error.get("type", "Erro de análise"))) for error in errors]
if data is None and outcome != "skipped":
    summary += ["", "⚠️ O relatório JSON está ausente ou inválido; isso não significa ausência de vulnerabilidades."]
with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
    output.write("\n".join(summary) + "\n")
