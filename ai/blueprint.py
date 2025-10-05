from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from .script_breakdown import breakdown_script
from .budget_analyzer import predict_budget_from_breakdown
from .task_assigner import assign_tasks_from_breakdown
from .scheduler import predict_shoot_schedule
from .reports import generate_report
from .utils import OUTPUT_DIR, MODELS_DIR, ensure_dirs
import tempfile

bp = Blueprint('ai', __name__, url_prefix='/ai')


@bp.route('/predict', methods=['POST'])
def predict():
    ensure_dirs()
    # Accept either file upload (file) or raw text (text)
    if 'file' in request.files:
        f = request.files['file']
        fn = secure_filename(f.filename or 'upload.pdf')
        tmp = Path(tempfile.gettempdir()) / fn
        f.save(str(tmp))
        breakdown_path = breakdown_script(str(tmp), out_name=f'{fn}.json')
    elif request.json and 'text' in request.json:
        txt = request.json['text']
        tmp = Path(tempfile.gettempdir()) / 'upload.txt'
        tmp.write_text(txt, encoding='utf8')
        breakdown_path = breakdown_script(str(tmp), out_name='upload.json')
    else:
        return jsonify({'error': 'no file or text provided'}), 400

    import json
    bd = json.loads(breakdown_path.read_text(encoding='utf8'))
    budget = predict_budget_from_breakdown(bd)
    # simple demo crew list
    crew = [{'crew_id': f'C{i}', 'name': f'Crew{i}'} for i in range(1, 6)]
    tasks = assign_tasks_from_breakdown(bd, crew)
    schedule_path = predict_shoot_schedule([{'task': t['scene_index'], 'duration_days': 1, 'assigned_to': t['assigned_to']} for t in tasks])
    report_paths = generate_report(bd, budget, tasks, schedule_path, out_name=f'report_{breakdown_path.stem}')

    return jsonify({'breakdown': str(breakdown_path), 'budget': budget, 'tasks': tasks, 'schedule': str(schedule_path), 'report': report_paths})
