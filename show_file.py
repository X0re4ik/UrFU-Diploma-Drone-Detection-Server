import matplotlib.pyplot as plt
import torch
import numpy as np
from collections import defaultdict

# Данные
drone_detection_statistics = {
    0: [{"confidence": torch.tensor(0.8299), "class_id": "Aircraft-Type-UAV"}],
    1: [{"confidence": torch.tensor(0.8548), "class_id": "Aircraft-Type-UAV"}],
    2: [{"confidence": torch.tensor(0.7695), "class_id": "Aircraft-Type-UAV"}],
    3: [{"confidence": torch.tensor(0.7679), "class_id": "Aircraft-Type-UAV"}],
    4: [{"confidence": torch.tensor(0.8746), "class_id": "Aircraft-Type-UAV"}],
    5: [{"confidence": torch.tensor(0.8681), "class_id": "Aircraft-Type-UAV"}],
    6: [{"confidence": torch.tensor(0.8121), "class_id": "Aircraft-Type-UAV"}],
}

drone_model_statistics = defaultdict(list, {
    0: [{"confidence": torch.tensor([0.8022]), "model_id": "Bayraktar TB2"}],
    1: [{"confidence": torch.tensor([0.7376]), "model_id": "Bayraktar TB2"}],
    2: [{"confidence": torch.tensor([0.7462]), "model_id": "2323"}],
    3: [{"confidence": torch.tensor([0.4889]), "model_id": "Bayraktar TB2"}],
    4: [{"confidence": torch.tensor([0.7140]), "model_id": "Bayraktar TB2"}],
    5: [{"confidence": torch.tensor([0.5403]), "model_id": "Bayraktar TB2"}],
    6: [{"confidence": torch.tensor([0.5403]), "model_id": "Bayraktar TB2"}]
})

# Подготовка данных
frames = np.array(sorted(drone_detection_statistics.keys()))
detection_confidences = [d[0]['confidence'].item() for d in drone_detection_statistics.values()]
model_confidences = [d[0]['confidence'].item() for _, d in sorted(drone_model_statistics.items())]

# Подсчёт типов дронов
model_counts = defaultdict(int)
for frame_data in drone_model_statistics.values():
    for detection in frame_data:
        model_counts[detection['model_id']] += 1

# Подсчёт количества дронов по кадрам
drones_per_frame = [len(d) for d in drone_detection_statistics.values()]

# Создание фигуры
plt.figure(figsize=(15, 10))

# 1. График уверенности обнаружения дрона
plt.subplot(2, 2, 1)
bars_det = plt.bar(frames, detection_confidences, color='skyblue', width=0.6)
plt.title('Уверенность обнаружения дрона', fontsize=12)
plt.xlabel('Номер кадра', fontsize=10)
plt.ylabel('Confidence', fontsize=10)
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar in bars_det:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.3f}', ha='center', va='bottom', fontsize=8)

# 2. График уверенности модели
plt.subplot(2, 2, 2)
bars_model = plt.bar(frames, model_confidences, color='salmon', width=0.6)
plt.title('Уверенность определения модели', fontsize=12)
plt.xlabel('Номер кадра', fontsize=10)
plt.ylabel('Confidence', fontsize=10)
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
for i, (bar, model) in enumerate(zip(bars_model, [d[0]['model_id'] for _, d in sorted(drone_model_statistics.items())])):
    height = bar.get_height()
    color = 'red' if model == '2323' else 'salmon'
    bar.set_color(color)
    plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.3f}\n({model})', ha='center', va='bottom', fontsize=8)

# 3. Распределение типов дронов (теперь bar chart)
plt.subplot(2, 2, 3)
models = list(model_counts.keys())
counts = list(model_counts.values())
colors = ['salmon' if model == 'Bayraktar TB2' else 'red' for model in models]
bars_types = plt.bar(models, counts, color=colors, width=0.6)
plt.title('Распределение типов дронов', fontsize=12)
plt.xlabel('Модель дрона', fontsize=10)
plt.ylabel('Количество', fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar in bars_types:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height, f'{height}', ha='center', va='bottom', fontsize=10)

# 4. Количество дронов по кадрам
plt.subplot(2, 2, 4)
bars_count = plt.bar(frames, drones_per_frame, color='lightgreen', width=0.6)
plt.title('Количество дронов по кадрам', fontsize=12)
plt.xlabel('Номер кадра', fontsize=10)
plt.ylabel('Количество', fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar in bars_count:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height, f'{height}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()