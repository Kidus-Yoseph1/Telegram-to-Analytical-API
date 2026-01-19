import os 
import pandas as pd
from ultralytics import YOLO


def detect(image_dir):
    model = YOLO("yolov8n.pt")
    results = model.predict(source=image_path, stream= True, save = True, conf=0.5)
    detection_data = []
    product_labels = [
        # Medical & Pharmaceuticals 
        'pill', 'capsule', 'softgel', 'blister_pack', 'syrup_bottle', 
        'suspension_bottle', 'vial', 'ampoule', 'ointment_tube', 
        'medicine_box', 'inhaler', 'insulin_pen', 'eye_drop_bottle', 
        'suppository', 'bandage', 'thermometer', 'medical_gloves', 'cell phone','bottle',
        
        # Cosmetics & Beauty 
        'lipstick', 'mascara', 'eyeliner', 'foundation_bottle', 
        'cosmetic_jar', 'serum_dropper', 'perfume_bottle', 
        'makeup_palette', 'sachet', 'shampoo_bottle', 'sunblock_tube',
        
        # Identification & Quality 
        'barcode', 'expiry_date', 'qr_code'
    ]

    for result in results:
        img_name = os.path.basename(result.path)
        labels = [model.names[int(box.cls[0])] for box in result.boxes]
        confidences = [float(box.conf[0]) for box in result.boxes]


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
            'image_name': img_name,
            'detected_objects': ", ".join(labels),
            'max_confidence': max(confidences) if confidences else 0,
            'image_category': category
        })
    df = pd.DataFrame(detection_data)
    df.to_csv('enriched_detection_objects.csv', index=False)

if __name__ == "__main__":
    image_path = 'data/raw/images/**/*.jpg'
    detect(image_path)
