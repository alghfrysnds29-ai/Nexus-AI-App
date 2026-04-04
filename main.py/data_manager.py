import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_huge_database(file_name="huge_nexus_data.csv", rows=50000):
    """توليد قاعدة بيانات ضخمة ومنوعة للمخزون والمبيعات"""
    np.random.seed(42)
    
    categories = ['إلكترونيات', 'مستحضرات تجميل', 'أدوات منزلية', 'أزياء', 'ألعاب أطفال', 'قرطاسية']
    suppliers = [f'المورد {i}' for i in range(1, 51)] # 50 مورد مختلف
    
    # توليد تواريخ على مدار سنتين لزيادة الضخامة
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    random_dates = [start_date + timedelta(days=np.random.randint(0, 730)) for _ in range(rows)]
    
    data = {
        "تاريخ الطلب": random_dates,
        "المنتج": [f"منتج ذكي رقم {i}" for i in range(1, rows + 1)],
        "التصنيف": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(0, 2000, rows),
        "كمية المبيعات": np.random.randint(1, 500, rows),
        "تكلفة الوحدة": np.random.uniform(10, 5000, rows).round(2),
        "سعر البيع": np.random.uniform(15, 10000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(2, 45, rows),
        "المرتجعات": np.random.randint(0, 20, rows)
    }
    
    df = pd.DataFrame(data)
    # ضمان منطقية السعر (سعر البيع دائماً أعلى من التكلفة بنسبة ربح)
    df['سعر البيع'] = (df['تكلفة الوحدة'] * np.random.uniform(1.2, 2.5, rows)).round(2)
    
    # حفظ الملف في المجلد
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"✅ تم إنشاء قاعدة بيانات بـ {rows} سطر بنجاح في ملف: {file_name}")
    return df

if __name__ == "__main__":
    # تشغيل هذا الملف منفرداً سينتج لك القاعدة الضخمة فوراً
    create_huge_database()
