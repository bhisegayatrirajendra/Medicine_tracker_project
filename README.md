🩺 Project Title:

Medicine Tracker Website

🌐 Project Overvie:

The Medicine Tracker Website is a web-based application designed to help users quickly locate pharmacies or medical stores that have a specific medicine available in their inventory.

By simply entering the medicine name and city name, the system provides a list of nearby pharmacies where that medicine is in stock, along with important details such as the pharmacy name, address, contact information, and distance.

This website aims to make it easier for users to find medicines, especially during emergencies, without having to visit multiple stores physically.

🎯 Objectives:

To help users find required medicines easily within their city.

To save time and effort by providing nearby medical store details online.

To build a centralized platform connecting users and pharmacies.

To allow pharmacies to update and manage their medicine stock.

To support location-based search for better accuracy.

⚙️ System Modules / Features:
🧍‍♀️ 1. User Module:

Users can search medicines using medicine name and city name.

Displays list of nearby pharmacies where medicine is available.

View pharmacy details: name, address, contact, and available stock.

Option to view location on map (Google Maps integration).

Simple and user-friendly web interface.

🏪 2. Pharmacy Module:

Pharmacy registration and login.

Ability to add, update, or delete medicine stock.

View user searches related to their medicines.


🧭 Working Process / Flow:

The user opens the website and enters the medicine name and city.

The system searches the database for pharmacies in that city that have the medicine in stock.

A list of available pharmacies is displayed with details and map locations.

The user can contact or navigate to the desired pharmacy directly.

💻 Technology Stack:
Component	Technology Used
Frontend	HTML, CSS, JavaScript, Bootstrap 
Backend	Python 
Database	MySQL 

✅ Advantages:

Real-time medicine availability for users.

Saves time and effort in finding medicines.

Improves connectivity between users and pharmacies.

Reduces crowding and unnecessary travel.


⚠️ Limitations:

Data accuracy depends on pharmacy updates.

Limited to registered pharmacies only.

🚀 Future Enhancements:

Add online ordering and home delivery features.

Allow prescription uploads for faster medicine search.

Integrate AI-based suggestion system for alternate medicines.

Enable push notifications when a medicine becomes available nearby.

🗂️ ✅ Project Folder Structure

Medicine_Tracker/
│
├── server.py                     
│
├── templates/                    
│   ├── index.html
│   ├── pharmacist_login.html
│   ├── pharmacist_register.html
│   ├── pharmacist_dashboard.html
│   ├── add_medicine.html
│   ├── edit_medicine.html
│   ├── forgot_password.html
│
└── static/                     
    ├── style.css
    ├── bg.jpg                     
    ├── js/                     
    └── images/                 
