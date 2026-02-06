# 🤖 Robot Delivery - Control System

A complete robot control system with separated frontend and backend architecture.

## 🏗️ Architecture

- **Backend:** Django REST API (Port 8000)
- **Frontend:** Vanilla JavaScript SPA (Port 8080)
- **Communication:** REST API with CORS enabled

## 🚀 Quick Start

### Option 1: Use Start Script (Recommended)

```bash
cd Robot_Delivery
./start.sh
```

Then open: `http://localhost:8080`

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd Robot_Delivery
python3 manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd Robot_Delivery/frontend
python3 -m http.server 8080
```

Then open: `http://localhost:8080`

## 📦 Installation

```bash
# Install backend dependencies
pip3 install -r requirements.txt

# Run migrations
python3 manage.py makemigrations
python3 manage.py migrate
```

## 📁 Project Structure

```
Robot_Delivery/
├── frontend/              # Frontend application (NEW)
│   ├── index.html        # Main HTML
│   ├── styles.css        # All styles
│   ├── app.js            # JavaScript logic
│   └── README.md         # Frontend docs
│
├── django_app/           # Backend API
│   ├── models.py         # Position, Endpoint models
│   ├── views.py          # API endpoints
│   └── urls.py           # API routes
│
├── config/               # Django settings
│   └── settings.py       # CORS enabled
│
├── start.sh              # Start both services
└── README.md             # This file
```

## 🎯 Features

### ✅ Robot Control
- View all delivery positions
- Send robot to specific points
- Real-time status updates
- Visual asterisk indicator

### ✅ Token Management
- OAuth token refresh
- Automatic token usage in API calls
- Token stored globally

### ✅ Endpoint Manager
- Create custom API endpoints
- Test with GET/POST/PUT/DELETE
- Save for reuse
- View formatted responses

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/positions/` | GET | List all positions |
| `/api/positions/create/` | POST | Create position |
| `/api/robot/call/` | POST | Send robot |
| `/api/token/refresh/` | POST | Refresh OAuth token |
| `/api/endpoints/` | GET | List saved endpoints |
| `/api/endpoints/create/` | POST | Create endpoint |
| `/api/endpoints/{id}/execute/` | POST | Execute endpoint |

## 🔧 Configuration

### Backend API URL

Edit `frontend/app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### CORS Settings

Edit `config/settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Development
# For production:
# CORS_ALLOWED_ORIGINS = ["https://your-domain.com"]
```

## 📚 Documentation

- **Frontend:** See `frontend/README.md`
- **Architecture:** See `ARQUITECTURA_SEPARADA.md`
- **Endpoints:** See `API_EXAMPLES.md`
- **Token Refresh:** See `REFRESH_TOKEN.md`
- **Endpoint Manager:** See `ENDPOINT_MANAGER.md`

## 🎨 Technologies

### Backend
- Django 5.0.1
- Django CORS Headers
- Requests library
- SQLite database

### Frontend
- Vanilla JavaScript (ES6+)
- Fetch API
- CSS Flexbox
- No frameworks - pure web tech

## 🔒 Security Notes

**Current setup is for DEVELOPMENT:**
- CORS allows all origins
- No authentication required
- All endpoints are public

**For production, implement:**
- JWT authentication
- Restrict CORS to specific domains
- Use HTTPS
- Add rate limiting

## 🐛 Troubleshooting

### "Failed to fetch" error
Backend not running. Start with: `python3 manage.py runserver`

### "CORS policy" error
1. Check `corsheaders` in INSTALLED_APPS
2. Restart Django server
3. Clear browser cache

### Port already in use
```bash
# Kill existing processes
pkill -f "python3 manage.py runserver"
pkill -f "python3 -m http.server"
```

## 🎓 Learning Resources

This project demonstrates:
- REST API architecture
- Frontend/Backend separation
- CORS configuration
- Fetch API usage
- Modern web development patterns

Perfect for learning full-stack development!

## 📞 Support

Check documentation files:
- `ARQUITECTURA_SEPARADA.md` - Architecture details
- `frontend/README.md` - Frontend specifics
- Other `.md` files for features

## ✨ Next Steps

1. ✅ Add user authentication (JWT)
2. ✅ Deploy frontend to Netlify/Vercel
3. ✅ Deploy backend to Heroku/AWS
4. ✅ Migrate to React/Vue for better state management
5. ✅ Add WebSocket for real-time updates

---

Made with ❤️ for robot delivery control
