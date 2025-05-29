# 🐾 Intelligent Pet Management System

## 📋 Project Overview

The Intelligent Pet Management System is a professional pet health management platform based on **Django + DeepSeek AI**, providing comprehensive AI intelligent consultation, health monitoring, detailed record management, and data visualization analysis services for pet owners.

### 🌟 Core Features
- **🤖 AI Intelligent Analysis**: Integrated DeepSeek AI engine providing professional pet health analysis and care recommendations
- **📊 Data Visualization**: Chart.js-driven interactive charts for intuitive pet health trend display
- **📝 Smart Logging**: Complete daily record management supporting multi-dimensional tracking of weight, mood, activity, etc.
- **🔍 Multi-scenario Consultation**: Comprehensive professional consultation covering daily feeding, vaccination, health behavior, emergency handling, etc.
- **🛡️ Security Protection**: Multi-layered content security checks ensuring platform safety
- **📱 Responsive Design**: Bootstrap framework support, perfectly adapted to various devices

### 💡 Technical Highlights
- **Modular Architecture**: Five core applications running independently with clear responsibilities, easy to maintain and extend
- **Smart Reminder System**: Personalized care reminders based on data analysis
- **Soft Delete Mechanism**: Safe data management supporting data recovery
- **Asynchronous Processing**: AJAX-supported refresh-free operations enhancing user experience
- **Data-Driven Decisions**: Intelligent analysis and recommendations based on historical data



## ⚡ Quick Start

### One-Click Launch (Recommended)
```bash
# 1. Clone the project
git clone -b yxk https://gitee.com/ywhitegoose/pet_-management.git
cd pet_management_yxk

# 2. Copy environment template
copy .env.example .env
# Edit .env file and set DEEPSEEK_API_KEY

# 3. One-click start
start_server_simple.bat
```

### Manual Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Database setup
cd pet_site
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Start development server
python manage.py runserver
```

## 📖 Instructions

### Core Modules
1. **Pet Profile Management**: Complete pet information management with photo upload
2. **Smart Logging**: Daily health data recording with AI analysis
3. **Data Visualization**: Interactive charts showing health trends
4. **AI Consultation**: Professional pet care advice powered by DeepSeek AI
5. **User Management**: Secure authentication and data isolation

#### Contribution

1.  Fork the repository
2.  Create Feat_xxx branch
3.  Commit your code
4.  Create Pull Request


#### Gitee Feature

1.  You can use Readme\_XXX.md to support different languages, such as Readme\_en.md, Readme\_zh.md
2.  Gitee blog [blog.gitee.com](https://blog.gitee.com)
3.  Explore open source project [https://gitee.com/explore](https://gitee.com/explore)
4.  The most valuable open source project [GVP](https://gitee.com/gvp)
5.  The manual of Gitee [https://gitee.com/help](https://gitee.com/help)
6.  The most popular members  [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
