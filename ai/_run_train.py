import sys
from pathlib import Path
ai_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(ai_dir))
import train_model
train_model.train_from_dataset(str(ai_dir / 'dataset.csv'))
print('Training finished')
