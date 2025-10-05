from pathlib import Path
from typing import Dict, Any
from .utils import REPORTS_DIR, save_json, ensure_dirs


def generate_report(breakdown: Dict[str, Any], budget: Dict[str, Any], tasks: Dict[str, Any], schedule_path: Path, out_name: str = 'report') -> Dict[str, Path]:
    ensure_dirs()
    rpt = {
        'breakdown': breakdown,
        'budget': budget,
        'tasks': tasks,
        'schedule_file': str(schedule_path),
    }
    json_path = REPORTS_DIR / f'{out_name}.json'
    save_json(rpt, json_path)

    pdf_path = REPORTS_DIR / f'{out_name}.pdf'
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont('Helvetica', 12)
        c.drawString(50, 750, f"Report: {out_name}")
        c.drawString(50, 730, f"Predicted budget: {budget.get('predicted_budget')}")
        c.drawString(50, 710, f"Num scenes: {breakdown.get('num_scenes')}")
        c.save()
    except Exception:
        # reportlab not available — skip PDF generation
        pdf_path = None

    return {'json': json_path, 'pdf': pdf_path}


if __name__ == '__main__':
    ensure_dirs()
    print('Reports module ready')
