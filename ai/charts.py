from typing import List, Dict, Any
from pathlib import Path
import matplotlib.pyplot as plt
from .utils import CHARTS_DIR, ensure_dirs


def generate_performance_chart(data: Dict[str, List[float]], out_name: str = 'performance.png') -> Path:
    """data: {'x': [...], 'predicted': [...], 'actual': [...]}"""
    ensure_dirs()
    x = data.get('x', list(range(len(data.get('predicted', [])))))
    predicted = data.get('predicted', [])
    actual = data.get('actual', [])
    plt.figure(figsize=(8, 4))
    plt.plot(x, predicted, label='Predicted', marker='o')
    plt.plot(x, actual, label='Actual', marker='x')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    out = CHARTS_DIR / out_name
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


if __name__ == '__main__':
    ensure_dirs()
    out = generate_performance_chart({'predicted': [1, 2, 3, 4], 'actual': [1, 1.5, 2.5, 4], 'x': [0,1,2,3]})
    print('Saved chart to', out)
