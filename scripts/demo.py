import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Résolution automatique de CAPTCHA")


# Charger les modèles depuis l'API

with st.spinner("Chargement des modèles OCR..."):
    info = requests.get(f"{API_URL}/captcha/model-info").json()
    models = info["models"]

labels = [m["label"] for m in models]
default_label = next(
    (m["label"] for m in models if m.get("default")),
    labels[0]
)

model_label = st.selectbox(
    "Modèle OCR",
    labels,
    index=labels.index(default_label)
)

# Modèle sélectionné
selected_model = next(
    m for m in models if m["label"] == model_label
)

model_key = selected_model["key"]

# Infos modèle

with st.expander("ℹInformations sur le modèle sélectionné", expanded=True):
    st.markdown(f"**Nom :** {selected_model['label']}")
    st.markdown(f"**Description :** {selected_model.get('description', '—')}")
    if selected_model.get("default"):
        st.markdown("⭐ **Modèle recommandé par défaut**")


# URL cible

url = st.text_input(
    "URL contenant un CAPTCHA",
    #https://solvecaptcha.com/demo/image-captcha
    #https://rutracker.org/forum/profile.php?mode=register
)


# Action
if st.button("Résoudre le CAPTCHA"):
    with st.spinner("Résolution en cours..."):
        try:
            r = requests.post(
                f"{API_URL}/captcha/solve-and-submit",
                params={
                    "url": url,
                    "model": model_key
                },
                timeout=300
            )
            data = r.json()

            status = data.get("status")
            prediction = data.get("prediction")
            duration = data.get("duration_sec")
            captcha_path = data.get("captcha_path")

            if status == "success":
                st.success("✅ CAPTCHA accepté par le site")
            elif status == "rejected":
                st.error("❌ CAPTCHA rejeté par le site")
            elif status == "uncertain":
                st.warning("⚠️ CAPTCHA soumis, mais résultat non confirmé")
            else:
                st.error(f"💥 Erreur technique : {data.get('reason')}")

            if prediction:
                st.write("Texte détecté :", prediction)

            if duration:
                st.write("⏱ Temps :", round(duration, 2), "secondes")

            if captcha_path:
                st.image(captcha_path, caption="CAPTCHA détecté")

        except requests.exceptions.Timeout:
            st.error("⏳ Temps dépassé : le site met trop de temps à répondre")
        except Exception as e:
            st.error(f"💥 Erreur inattendue : {e}")
