def detect_dirty_floor(results, conf_threshold=0.25):
    """
    results = model(frame)[0]
    Return: (is_dirty: bool, confidence: float)
    """
    max_conf = 0.0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results.names[cls_id].lower()

        if conf >= conf_threshold and ("dirty" in label or "kotor" in label):
            max_conf = max(max_conf, conf)

    return max_conf > 0, max_conf
