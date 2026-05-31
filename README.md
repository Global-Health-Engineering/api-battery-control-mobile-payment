<p align="center">
  <img width="538" alt="System Image" src="https://github.com/user-attachments/assets/a7082a3b-5d5e-4192-bf68-f2cdd62629f4" />
</p>

## ORCiD
0009-0008-3294-6200

## PAYG Charging System – Prototype

This project presents a complete prototype of a **Pay-As-You-Go (PAYG) charging system** designed to enable flexible, low-cost access to energy without requiring fixed infrastructure or battery swapping.

The system allows users to **start and pay for charging sessions via mobile payment and messaging platforms (e.g. WhatsApp)**. Once a payment is completed, the backend authorizes the charging process, and the connected hardware enables power delivery accordingly.

This repository contains all components required to understand and reproduce the system:
- **Backend (Flask API)** for payment validation, session control, and charger communication  
- **Hardware firmware (MicroPython)** for device-side control and communication  
- **CAD files** for the physical enclosure of the charging unit  
- **System architecture and workflow logic** for end-to-end PAYGO operation  

The solution focuses on **simplicity, scalability, and affordability**, making it suitable for environments where traditional charging infrastructure is not feasible.

---

### Key Features
- Pay-As-You-Go charging (no subscription required)  
- Mobile payment integration (e.g. M-Pesa)  
- Remote session activation via messaging platforms  
- Low hardware complexity and cost  
- No fixed infrastructure required  
- Scalable and adaptable system design  

---

### Purpose
This prototype demonstrates a **practical alternative to battery swapping and conventional charging systems**, with the goal of improving accessibility to energy through a flexible PAYGO model.

---

### Status
Fully functional prototype including hardware, backend, and enclosure design.

<p align="center">
  <img width="4538" alt="Architecture Flow" src="https://github.com/user-attachments/assets/3687777d-e19b-4cc9-97c7-ead42448e0a9" />
</p>
