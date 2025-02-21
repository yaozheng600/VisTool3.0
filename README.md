# A Data Visualization Tool for Finding Optimal Privacy-Utility Trade-off in Data Analysis

## Master Thesis at the Institute for Computer Science, Freie Universität Berlin
**Research Group:** Human-Centered Computing (HCC)  
**Author:** Zheng Yao  
**Supervisors:** Dr. Daniel Franzen, Prof. Dr. C. Müller-Birn, Prof. Dr. Volker Roth  
**Date:** February 21, 2025  

---

## 📖 Abstract
With the increasing importance of data dissemination, concerns about privacy breaches have prompted the development of data anonymization techniques. However, these techniques often come at the expense of data utility. This thesis presents a novel approach to balancing privacy and utility in data anonymization by integrating both aspects into a unified framework and visualizing trade-offs.

The study introduces **VisTool**, a prototype that quantifies privacy and utility losses during data anonymization and offers intuitive visualizations to assist users in making informed decisions. Through various visualization methods and user interface components, **VisTool** enables a clear understanding of different anonymization strategies and their trade-offs.

This research addresses the gap in visualization-supported privacy-utility trade-offs and proposes a user-friendly tool for data controllers. Evaluations demonstrate the prototype's effectiveness in achieving an optimal balance between privacy and utility.

---

## 🎯 Research Goals
1. **Develop a visualization-supported tool** that helps data controllers balance privacy and utility in data anonymization.
2. **Integrate privacy and utility considerations** within a single framework for more informed decision-making.
3. **Provide intuitive visualizations** to illustrate the trade-offs between different anonymization strategies.
4. **Evaluate usability and effectiveness** through case studies and user testing.

---

## 🛠 Implementation
### 🔹 Anonymization Methods
- **k-Anonymity**
- **l-Diversity**
- **t-Closeness**

### 🔹 Core Algorithm
- **Mondrian Algorithm** for partitioning and anonymization
- **Privacy Criteria Control (PCC)** for automatic privacy parameter adjustment

### 🔹 Visualization Components
- **Scatter Plot** for visualizing privacy-utility trade-offs
- **Numerical Indicators** for privacy and utility loss
- **Interactive UI** for selecting anonymization strategies

---
## 🏗 Technology Stack

The project was implemented using the following technologies:

- **Programming Language** Python 3.x

- **Frameworks & Libraries** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, Streamlit, Plotly

- **Data Processing** Mondrian Algorithm for anonymization, Privacy Criteria Control (PCC)

- **Visualization** Matplotlib, Seaborn for data representation

- **Development Tools** Jupyter Notebook, PyCharm, Git for version control
---
## 📊 Evaluation & Results
The effectiveness of **VisTool** was assessed through:
- **Case Studies:** Testing with various datasets to analyze the distribution of trade-offs.
- **Usability Tests:** Evaluating efficiency, effectiveness, and user satisfaction using System Usability Scale (SUS) and After Scenarios Questionnaire (ASQ).
- **Comparative Experiments:** Comparing traditional anonymization approaches with the visualization-supported approach.

Results show that **VisTool** provides a more effective and user-friendly method for selecting optimal privacy-utility trade-offs compared to traditional heuristic approaches.

---

## 📌 Repository Contents
- **`Anony/`** - Source code for VisTool
- **`main.py/`** - Dashboard of VisTool
- **`README.md`** - Project overview (this file)


---

## 📜 License
This project is licensed under the MIT License.

---

## ✉ Contact
For any inquiries, feel free to contact me at:  
📧 Email: zheng.yao@gmx.de

---

## 🌟 Acknowledgments
This work was carried out as part of my Master’s Thesis at Freie Universität Berlin under the supervision of Dr. Daniel Franzen. I extend my gratitude to my advisors and the Human-Centered Computing research group for their guidance and support.

