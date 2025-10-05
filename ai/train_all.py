from .utils import ensure_dirs
from .budget_analyzer import train_budget_model
from .task_assigner import train_task_assigner


def train_all(force: bool = False):
    ensure_dirs()
    p1 = train_budget_model(force=force)
    p2 = train_task_assigner(force=force)
    return {'budget_model': str(p1), 'task_assigner': str(p2)}


if __name__ == '__main__':
    print('Training all models (this may take a moment)')
    res = train_all()
    print('Trained:', res)
