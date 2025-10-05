import json
from pathlib import Path
from ai.script_breakdown import breakdown_script
from ai.budget_analyzer import train_budget_model, predict_budget_from_breakdown
from ai.task_assigner import train_task_assigner, assign_tasks_from_breakdown
from ai.scheduler import predict_shoot_schedule
from ai.reports import generate_report


def test_pipeline_end_to_end(tmp_path):
    # Use a small text file as input
    txt = tmp_path / 'sample.txt'
    txt.write_text('INT. HOUSE - DAY\nJOHN\nHello.\nEXT. PARK - NIGHT\nCHASE and EXPLOSION.')

    bd_path = breakdown_script(str(txt), out_name='test_breakdown.json')
    bd = json.loads(bd_path.read_text(encoding='utf8'))

    # ensure models trained
    train_budget_model(force=True)
    train_task_assigner(force=True)

    budget = predict_budget_from_breakdown(bd)
    assert 'predicted_budget' in budget

    crew = [{'crew_id': 'C1'}, {'crew_id': 'C2'}]
    tasks = assign_tasks_from_breakdown(bd, crew)
    assert isinstance(tasks, list)

    schedule = predict_shoot_schedule([{'task': 't1', 'duration_days': 1, 'assigned_to': 'C1'}], start_date=None)
    assert schedule.exists()

    report = generate_report(bd, budget, tasks, schedule, out_name='test_report')
    assert report['json'].exists()
