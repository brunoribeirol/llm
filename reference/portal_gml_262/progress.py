"""Portable study notebook; no promise of persistence on ephemeral hosting."""
import json


def export_notebook(completed, notes):
    return json.dumps({"version": 1, "completed": sorted(completed), "notes": notes}, ensure_ascii=False, indent=2)


def import_notebook(payload):
    if len(payload) > 200_000:
        raise ValueError("O arquivo deve ter no máximo 200 KB.")
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("O arquivo não contém JSON válido.") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Formato de caderno desconhecido.")
    completed = data.get("completed", [])
    notes = data.get("notes", {})
    if not isinstance(completed, list) or any(type(x) is not int or x not in range(31) for x in completed):
        raise ValueError("A lista de aulas concluídas é inválida.")
    if not isinstance(notes, dict) or any(k not in {str(i) for i in range(31)} or not isinstance(v, str) or len(v) > 10000 for k, v in notes.items()):
        raise ValueError("As anotações devem corresponder às aulas 00 a 30, com até 10 mil caracteres por aula.")
    return set(completed), notes
