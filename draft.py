from utils.plots import convert_name_id

info = [{'xmin': 192, 'ymin': 399, 'xmax': 219, 'ymax': 427, 'score': '0.81', 'label': 'Vehicle'}, {'xmin': 244, 'ymin': 419, 'xmax': 267, 'ymax': 451, 'score': '0.82', 'label': 'Fire'}, {'xmin': 138, 'ymin': 179, 'xmax': 352, 'ymax': 441, 'score': '0.93', 'label': 'Smoke'}]

# Initialize an empty dictionary to store label counts
label_counts = {}

# Iterate over each dictionary in the list
for item in info:
    label = item['label']
    # Increment the count for the label
    label_counts[label] = label_counts.get(label, 0) + 1

print(label_counts)
# Print the label counts
message = []
for label, count in label_counts.items():
    vn_label = convert_name_id(label, 'vietnamese_name')
    s = f"Phát hiện {count} {vn_label}"
    message.append(s)

print(message)