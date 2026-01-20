import os
import pandas as pd
from ultralytics import YOLO
from pathlib import Path
import torch
import gc

def detect(image_path_pattern):
    model = YOLO("yolov8n.pt")
    
    results = model.predict(source=image_path_pattern, stream=True, save=True, conf=0.5)
    
    detection_data = []
    
    product_labels = [
        'pill', 'capsule', 'softgel', 'blister_pack', 'syrup_bottle', 
        'suspension_bottle', 'vial', 'ampoule', 'ointment_tube', 
        'medicine_box', 'inhaler', 'insulin_pen', 'eye_drop_bottle', 
        'suppository', 'bandage', 'thermometer', 'medical_gloves', 'cell phone','bottle',
        'lipstick', 'mascara', 'eyeliner', 'foundation_bottle', 
        'cosmetic_jar', 'serum_dropper', 'perfume_bottle', 
        'makeup_palette', 'sachet', 'shampoo_bottle', 'sunblock_tube',
        'barcode', 'expiry_date', 'qr_code'
    ]

    print("🚀 Starting detection...")

    for i, result in enumerate(results):
        full_path = Path(result.path)
       
        parts = full_path.parts
        if 'data' in parts:
            relative_path = os.path.join(*parts[parts.index('data'):])
        else:
            relative_path = full_path.name 
            
        # Clean path for PostgreSQL (use forward slashes)
        clean_path = str(relative_path).replace("\\", "/")

        # Extract labels and confidences
        labels = [model.names[int(box.cls[0])] for box in result.boxes]
        confidences = [float(box.conf[0]) for box in result.boxes]

        # Classification Logic
        has_person = 'person' in labels
        has_product = any(item in labels for item in product_labels)
        
        if has_person and has_product:
            category = 'promotional_ad' 
        elif has_product:
            category = 'product_listing'
        elif has_person:
            category = 'lifestyle_shot'
        else:
            category = 'unclassified'
        
        detection_data.append({
            'image_path': clean_path,
            'detected_objects': ", ".join(labels),
            'max_confidence': max(confidences) if confidences else 0,
            'image_category': category
        })

        # CRASH PROTECTION: Clear RAM every 50 images
        if i % 50 == 0:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print(f"Processed {i} images...")

    df = pd.DataFrame(detection_data)
    df.to_csv('enriched_detection_objects.csv', index=False)
    print("CSV saved: enriched_detection_objects.csv")

if __name__ == "__main__":
    input_pattern = 'data/raw/images/**/*.jpg'
    detect(input_pattern)
