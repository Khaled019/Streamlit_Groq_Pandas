import streamlit as st
import pandas as pd
from groq import Groq
import io

# إعدادات الصفحة
st.set_page_config(page_title="مُعالج وصوف المنتجات الدفعي", page_icon="📦", layout="wide")

st.title("📦 مُنشئ وصوف المنتجات الذكي للدفعات (Bulk Generator)")
st.write("ارفع ملف Excel أو CSV يحتوي على قائمة منتجاتك، واحصل عليها كاملة مع وصوف السيو بضغطة زر واحدة.")

# إدخال مفتاح API من القائمة الجانبية
groq_api_key = st.sidebar.text_input("أدخل مفتاح Groq API الخاص بك:", type="password")
st.sidebar.markdown("[احصل على مفتاح مجاني من هنا](https://groq.com)")

# نموذج للملف المطلوب لتسهيل تجربة المستخدم
st.sidebar.markdown("---")
st.sidebar.subheader("💡 شكل الملف المطلوب:")
st.sidebar.write("يجب أن يحتوي ملفك على الأعمدة التالية تماماً:")
st.sidebar.code("اسم_المنتج\nالميزات\nالكلمات_المفتاحية")

# اختيار لهجة الكتابة العامة للدُفعة
tone = st.selectbox("اختر لهجة الكتابة لجميع المنتجات:", ["حماسية ومقنعة", "مهنية ورسمية", "بسيطة وودية", "فاخرة"])

# واجهة رفع الملفات
uploaded_file = st.file_uploader("اختر ملف Excel أو CSV (بحد أقصى 50 منتجاً لحماية حصتك الإعلانية):", type=["csv", "xlsx"])

def generate_seo_description(client, name, features, keywords, tone_style):
    """دالة برمجية للاتصال بـ Groq وتوليد الوصف لكل سطر"""
    prompt = f"""
    أنت خبير محترف في كتابة الإعلانات وتحسين محركات البحث (SEO) للمتاجر الإلكترونية.
    قم بكتابة وصف منتج احترافي وجذاب بناءً على المعلومات التالية:
    
    - اسم المنتج: {name}
    - الميزات والخصائص: {features}
    - الكلمات المفتاحية (SEO): {keywords}
    - لهجة النص: {tone_style}
    
    الهيكل المطلوب بدقة:
    1. مقدمة تسويقية تثير الرغبة (سطرين).
    2. قائمة منقّطة بالفوائد (Bullet points).
    3. وصف ميتا (Meta Description) مناسب لجوجل بطول بين 130-155 حرفاً يحتوي على الكلمة المفتاحية.
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "أنت مساعد مبيعات رقمي محترف تكتب باللغة العربية الفصحى وبشكل منظم جداً."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"حدث خطأ أثناء التوليد: {str(e)}"

# بدء المعالجة عند رفع الملف
if uploaded_file is not None:
    try:
        # قراءة الملف بناءً على صيغته
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # التحقق من وجود الأعمدة المطلوبة
        required_columns = ['اسم_المنتج', 'الميزات', 'الكلمات_المفتاحية']
        if not all(col in df.columns for col in required_columns):
            st.error(f"تنبيه: يجب أن يحتوي الملف على الأعمدة التالية بدقة: {required_columns}")
        else:
            # تحديد الحد الأقصى بـ 50 منتجاً
            if len(df) > 50:
                st.warning("الملف يحتوي على أكثر من 50 منتجاً. سيتم معالجة أول 50 منتجاً فقط حفاظاً على استقرار الأداة.")
                df = df.head(50)
            
            # عرض البيانات المرفوعة للمستخدم لمعاينتها
            st.subheader("👀 معاينة البيانات المرفوعة")
            st.dataframe(df, use_container_width=True)
            
            # زر بدء المعالجة الذكية
            if st.button("⚡ ابدأ توليد الوصف لجميع المنتجات دفعة واحدة"):
                if not groq_api_key:
                    st.error("من فضلك، أدخل مفتاح Groq API الخاص بك أولاً.")
                else:
                    client = Groq(api_key=groq_api_key)
                    
                    # إنشاء شريط تقدم مرئي للمستخدم
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # إضافة عمود جديد لنتائج الذكاء الاصطناعي
                    seo_descriptions = []
                    
                    for index, row in df.iterrows():
                        # تحديث حالة التقدم للمستخدم
                        current_progress = (index + 1) / len(df)
                        progress_bar.progress(current_progress)
                        status_text.text(f"جاري معالجة المنتج {index + 1} من أصل {len(df)}: {row['اسم_المنتج']}...")
                        
                        # استدعاء دالة التوليد
                        desc = generate_seo_description(
                            client, 
                            row['اسم_المنتج'], 
                            row['الميزات'], 
                            row['الكلمات_المفتاحية'], 
                            tone
                        )
                        seo_descriptions.append(desc)
                    
                    # حفظ النتائج في الجدول
                    df['وصف_SEO_المولد'] = seo_descriptions
                    
                    st.success("🎉 اكتملت المعالجة بنجاح لجميع المنتجات!")
                    st.dataframe(df[['اسم_المنتج', 'وصف_SEO_المولد']], use_container_width=True)
                    
                    # تجهيز ملف التنزيل وتحويله إلى بايتس (Bytes) دون حفظه على السيرفر
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='SEO Descriptions')
                    processed_data = output.getvalue()
                    
                    # زر تحميل الملف الناتج
                    st.download_button(
                        label="📥 تحميل ملف Excel الجاهز بالوصوف",
                        data=processed_data,
                        file_name="ready_seo_products.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
