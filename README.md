# 🧠 Earwax Accumulation Monitoring Model – Speaksi

A smart machine learning model built to support **speech-impaired** and **autistic** individuals by **monitoring earwax accumulation** through environmental and user-related factors — integrated with the [Speaksi](https://github.com/Subitsha2110/SpeakSi) app.

---

## 🧩 About the Model

**Earwax buildup** is a common challenge for hearing aid users, especially for those with speech impairments or autism, who may **forget or struggle** to clean their hearing devices regularly.

This ML model:
- Monitors the **daily rate of earwax accumulation** using real-world data like:
  - 🌡️ Temperature
  - 💧 Humidity
  - 🌿 Pollen count
  - 🧼 Dust level
  - 🧳 Travel activity
  - 🌸 Pollen season status
  - 🎂 Age of the user
- Uses a **daily tracking mechanism** that stores values in a MySQL database (`earwax_monitoring`).
- When **accumulation reaches 100%**, the system **automatically notifies the user** via the Speaksi app:  
  _"Time to clean your hearing aid!"_

---

## 📱 About Speaksi

[Speaksi](https://github.com/Subitsha2110/SpeakSi) is an AI-powered assistant application for:
- 🧑‍🦯 Deaf and mute individuals
- 🧠 Speech-impaired or autistic patients

### Features of Speaksi:
- 🗣️ **Magic Spell** – Detects and improves pronunciation accuracy.
- 🔤 **Speech-to-text conversion** – Translates spoken audio to readable text.
- 👄 **Lip-reading module** – Helps understand staggered or unclear speech.
- 🧼 **Earwax Monitoring** – Predicts when the user should clean their hearing aid using ML.

---

## 🧪 How It Works

1. **Real-time API integration** collects temperature, humidity, pollen, and dust data.
2. Daily readings are stored in `earwax_data` table inside `earwax_monitoring` MySQL database.
3. An ML model trained with environmental and user-profile data predicts **earwax percentage daily**.
4. Once the cumulative value reaches **100%**, the app triggers a **reminder notification**.

---

## 🛠️ Tech Stack

- **Python** – Model logic and API integration
- **Flask** – Backend API to serve the model
- **MySQL** – Persistent database to track user data and daily accumulation
- **Jupyter Notebook** – Model development and testing environment
- **VS Code** – App development environment
- **Real-time APIs** – For fetching live data (pollen, weather, etc.)

---

## 🧠 ML Model Inputs

| Feature          | Type   | Example          |
|------------------|--------|------------------|
| age              | int    | 25               |
| pollen           | float  | 6.2              |
| dust             | float  | 10.0             |
| humidity         | int    | 42               |
| temperature      | float  | 35.0             |
| traveling        | string | "Yes" or "No"    |
| pollen_season    | string | "Yes" or "No"    |

Output:
- `earwax_percentage`: Float (e.g., 4.5%, 9.0%, ...)

---

## 🔔 Notification Logic

When `SUM(earwax_percentage)` >= 100:
- Trigger in-app notification.
- Reset accumulation counter.



