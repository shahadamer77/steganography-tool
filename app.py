import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="كاشف ومُخفي البيانات في الصور", page_icon="🖼️", layout="centered")

st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🖼️ أداة الإخفاء والكشف الرقمي (Steganography)</h2>", unsafe_allow_html=True)
st.write("---")

def text_to_bin(text):
    return ''.join(format(ord(char), '08b') for char in text)

def bin_to_text(binary):
    bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
    text = ""
    for b in bytes_list:
        text += chr(int(b, 2))
    return text

def hide_text(image, secret_text):
    secret_text += "#####"
    binary_secret = text_to_bin(secret_text)
    
    img = image.convert("RGB")
    pixels = img.load()
    width, height = img.size
    
    data_index = 0
    data_length = len(binary_secret)
    
    new_img = img.copy()
    new_pixels = new_img.load()
    
    for y in range(height):
        for x in range(width):
            if data_index < data_length:
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_secret[data_index])
                data_index += 1
                new_pixels[x, y] = (r, g, b)
            else:
                break
        if data_index >= data_length:
            break
            
    return new_img

def extract_text(image):
    img = image.convert("RGB")
    pixels = img.load()
    width, height = img.size
    
    extracted_bin = ""
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            extracted_bin += str(r & 1)
            
            if len(extracted_bin) % 8 == 0:
                current_text = bin_to_text(extracted_bin)
                if "#####" in current_text:
                    return current_text.replace("#####", "")
                    
    return "❌ لم يتم العثور على أي رسالة مخفية داخل هذه الصورة."

tab1, tab2 = st.tabs(["🔐 إخفاء نص في صورة", "🔍 كشف واستخراج النص"])

with tab1:
    st.subheader("إخفاء رسالة سرية داخل صورة")
    uploaded_file = st.file_uploader("اختر صورة (PNG/JPG):", type=["png", "jpg", "jpeg"], key="hide_up")
    secret_message = st.text_area("اكتب الرسالة السرية المراد إخفاؤها:")
    
    if st.button("🔒 إخفاء الرسالة داخل الصورة"):
        if uploaded_file and secret_message:
            image = Image.open(uploaded_file)
            st.info("جاري معالجة الصورة وإخفاء النص...")
            
            stego_image = hide_text(image, secret_message)
            
            buf = io.BytesIO()
            stego_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.success("✅ تم إخفاء النص بنجاح داخل الصورة بدون تغيير شكلها!")
            st.download_button("📥 تحميل الصورة الجديدة المخفي بها النص", data=byte_im, file_name="stego_image.png", mime="image/png")
        else:
            st.warning("يرجى رفع صورة وكتابة رسالة أولاً.")

with tab2:
    st.subheader("فحص صورة واستخراج الرسالة المخفية")
    check_file = st.file_uploader("رفع الصورة المراد فحصها:", type=["png"], key="check_up")
    
    if st.button("🔎 فحص واستخراج البيانات"):
        if check_file:
            image = Image.open(check_file)
            result = extract_text(image)
            
            if result.startswith("❌"):
                st.error(result)
            else:
                st.success("🎉 تم العثور على الرسالة المخفية بنجاح!")
                st.code(result, language="text")
        else:
            st.warning("يرجى رفع صورة للفحص أولاً.")
