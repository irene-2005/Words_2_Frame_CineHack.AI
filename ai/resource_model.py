"""
Resource modeling helpers: crew workload, task cost, finance summary.

Lightweight, dependency-free utilities used by the resource API and tests.
"""

from typing import List, Dict, Any


def predict_overworked_crew(crew: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a list of crew status dicts with keys:
    crew_id, name, hours_assigned, max_hours, spare_hours, overworked (bool)
    """
    status: List[Dict[str, Any]] = []
    for c in crew:
        hours_assigned = float(c.get('hours_assigned', 0))
        max_hours = float(c.get('max_hours', c.get('standard_hours', 40)))
        spare = round(max_hours - hours_assigned, 2)
        status.append({
            'crew_id': c.get('crew_id'),
            'name': c.get('name'),
            'hours_assigned': hours_assigned,
            'max_hours': max_hours,
            'spare_hours': spare,
            'overworked': hours_assigned > max_hours,
        })
    return status


def recommend_reassignments(status_list: List[Dict[str, Any]], max_transfer_per_pair: float = 8.0) -> List[Dict[str, Any]]:
    """Given a status list (from predict_overworked_crew), return suggestions to shift hours.

    Each suggestion is a dict:
      - if transfer possible: {'from': id, 'to': id, 'hours': x, 'note': str}
      - if not enough spare: {'to': id, 'hours_needed': x, 'note': str}
    """
    over = [s for s in status_list if s.get('spare_hours', 0) < 0]
    under = [s for s in status_list if s.get('spare_hours', 0) > 0]
    under.sort(key=lambda x: x.get('spare_hours', 0), reverse=True)

    suggestions: List[Dict[str, Any]] = []

    for o in over:
        needed = round(abs(o.get('spare_hours', 0)), 2)
        if needed <= 0:
            continue

        for u in under:
            if needed <= 0:
                break
            available = round(u.get('spare_hours', 0), 2)
            if available <= 0:
                continue
            transfer = min(needed, available, max_transfer_per_pair)
            if transfer <= 0:
                continue

            suggestions.append({
                'from': u.get('crew_id'),
                'to': o.get('crew_id'),
                'hours': round(transfer, 2),
                'note': f"transfer {round(transfer,2)}h from {u.get('name') or u.get('crew_id')} "
                        f"to {o.get('name') or o.get('crew_id')}",
            })

            # update trackers
            u['spare_hours'] = round(u.get('spare_hours', 0) - transfer, 2)
            needed = round(needed - transfer, 2)

        if needed > 0:
            suggestions.append({
                'to': o.get('crew_id'),
                'hours_needed': round(needed, 2),
                'note': 'insufficient spare hours — consider hiring or approving overtime',
            })

    return suggestions


def estimate_task_cost(hours: float, rate_per_hour: float, overhead_pct: float = 0.2) -> Dict[str, float]:
    """Estimate direct, overhead, and total cost for a task."""
    hours = float(hours)
    rate = float(rate_per_hour)
    direct = hours * rate
    overhead = direct * float(overhead_pct)
    total = direct + overhead
    return {
        'hours': hours,
        'rate': rate,
        'direct': round(direct, 2),
        'overhead': round(overhead, 2),
        'total': round(total, 2),
    }


def finance_summary(tasks: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate finance numbers from tasks with 'hours' and 'rate' (or rate_per_hour)."""
    direct = 0.0
    overhead = 0.0
    for t in tasks:
        h = float(t.get('hours', 0))
        r = float(t.get('rate', t.get('rate_per_hour', 0)))
        o_pct = float(t.get('overhead_pct', 0.2))
        d = h * r
        direct += d
        overhead += d * o_pct
    total = direct + overhead
    return {
        'direct': round(direct, 2),
        'overhead': round(overhead, 2),
        'total': round(total, 2)
    }


def analyze_crew_and_suggest(crew_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze crew workload and provide reassignment suggestions."""
    status_list = predict_overworked_crew(crew_data)
    suggestions = recommend_reassignments(status_list)
    return {'status_list': status_list, 'suggestions': suggestions}


if __name__ == '__main__':
    sample = [
        {'crew_id': 'C1', 'name': 'Alice', 'hours_assigned': 45, 'max_hours': 40},
        {'crew_id': 'C2', 'name': 'Bob', 'hours_assigned': 30, 'max_hours': 40},
        {'crew_id': 'C3', 'name': 'Cara', 'hours_assigned': 50, 'max_hours': 48},
        {'crew_id': 'C4', 'name': 'Dan', 'hours_assigned': 20, 'max_hours': 40},
    ]

    print('Crew analysis/demo:')
    print(analyze_crew_and_suggest(sample))
    print('\nTask cost sample:', estimate_task_cost(10, 75))
    print('\nFinance summary sample:', finance_summary([
        {'hours': 10, 'rate': 75},
        {'hours': 5, 'rate': 100, 'overhead_pct': 0.15}
    ]))