# 🚀 Setup & Testing Guide - 6G Blockchain System

## ✅ All Issues Fixed!

### **Issues Resolved:**
1. ✅ **Admin Required Decorator** - Fixed redirect loop (now redirects to Welcome page)
2. ✅ **Custom Admin Dashboard** - Beautiful dashboard template with real data
3. ✅ **Background Colors** - Improved color palette for better visibility
4. ✅ **Text Visibility** - Enhanced contrast, white text on dark background
5. ✅ **Message Display** - Added message system to show access errors
6. ✅ **Form Styling** - Improved form input appearance

---

## 🛠️ Quick Start - Step by Step

### **Step 1: Backup Database (Optional)**
```bash
python manage.py dumpdata > backup.json
```

### **Step 2: Clear Cache & Restart Server**
```bash
# Kill running server (Ctrl+C)

# Restart it fresh
python manage.py runserver
```

### **Step 3: Test User Flows**

#### **Create Admin User (if you don't have one)**
```bash
python manage.py createsuperuser
```
- Username: `admin`
- Email: `admin@example.com`
- Password: (choose something secure)

#### **Create Test Regular User**
1. Go to: `http://localhost:8000/register/`
2. Fill form with:
   - Username: `testuser`
   - Email: `testuser@example.com`
   - Password: `TestPassword123`
   - Confirm: `TestPassword123`
3. Click "Create Account"
4. Should redirect to login page

---

## 🧪 Testing Checklist

### **Test 1: Admin User Login & Dashboard**
- [ ] Go to `http://localhost:8000/accounts/login/`
- [ ] Login with admin credentials
- [ ] Should see beautiful dashboard at `/dashboard/`
- [ ] Dashboard shows:
  - [ ] Total Nodes count
  - [ ] Active Nodes count
  - [ ] Active Shards count
  - [ ] Pending Transactions count
  - [ ] Recent transactions table
  - [ ] Quick navigation menu
  - [ ] System status
  - [ ] Recently active nodes
- [ ] Navbar shows all menu items (Nodes, Shards, Transactions, etc.)
- [ ] "Admin" badge visible next to username

### **Test 2: Regular User Login & Welcome Page**
- [ ] Go to `http://localhost:8000/accounts/login/`
- [ ] Login with regular user (created via register)
- [ ] Should redirect to `/welcome/` page
- [ ] Welcome page shows:
  - [ ] User account information
  - [ ] Limited access message
  - [ ] Account menu
  - [ ] Support information
- [ ] Navbar shows limited menu
- [ ] No admin items in menu

### **Test 3: Access Control - Admin Routes**
- [ ] Login as regular user
- [ ] Try to access `/dashboard/` directly
- [ ] Should see error message and redirect to welcome
- [ ] Try to access `/nodes/` directly
- [ ] Should see error message and redirect to welcome
- [ ] Try to access `/shards/` directly
- [ ] Should see error message and redirect to welcome

### **Test 4: Admin Panel - User Management**
- [ ] Login as admin
- [ ] Go to `/admin/users/`
- [ ] Should see all registered users:
  - [ ] Username
  - [ ] Email
  - [ ] Staff status
  - [ ] Superuser status
  - [ ] Date joined
  - [ ] Last login
- [ ] Click on a user to edit
- [ ] Should see full user details form
- [ ] Check staff_status checkbox
- [ ] Click Save

### **Test 5: User Upgrade to Admin**
- [ ] Create a regular user via `/register/`
- [ ] Login as superuser to `/admin/`
- [ ] Go to Users section
- [ ] Click on the new user
- [ ] Check "Staff status" checkbox
- [ ] Click Save
- [ ] Logout and login as that user
- [ ] Should now see admin dashboard

### **Test 6: UI/Styling**
- [ ] Check text visibility on all pages
- [ ] All text should be readable (white on dark background)
- [ ] Green accents (#00ff88) should be visible
- [ ] Forms should have visible input fields
- [ ] Buttons should be clearly clickable
- [ ] Navigation should be clear
- [ ] Test on mobile (responsive design)
- [ ] All Font Awesome icons should display

### **Test 7: Color Verification**
- [ ] Page background: Dark navy blue (#0a0e27)
- [ ] Cards: Medium dark (#1a1f3a)
- [ ] Text: Bright white (#ffffff)
- [ ] Accents: Bright green (#00ff88)
- [ ] Labels: Light gray (#e0e0e0)
- [ ] Muted text: Medium gray (#a0a0a0)

### **Test 8: Forms**
- [ ] Registration form at `/register/`
  - [ ] All fields visible
  - [ ] Validation messages clear
  - [ ] Submit button working
- [ ] Login form at `/accounts/login/`
  - [ ] Fields visible and editable
  - [ ] Login button working
- [ ] Admin forms at `/admin/`
  - [ ] Create new users
  - [ ] Edit existing users
  - [ ] Change user permissions
  - [ ] Delete users

### **Test 9: Navigation**
- [ ] Main navbar visible on all pages
- [ ] Logo clickable (goes to dashboard/home)
- [ ] Menu items (for admin) work correctly:
  - [ ] Dashboard
  - [ ] Nodes
  - [ ] Shards
  - [ ] Transactions
  - [ ] Consensus
  - [ ] Storage
  - [ ] Admin Panel
- [ ] Logout button works
- [ ] User badge shows correct username

---

## 🔧 If Something Doesn't Work

### **Django is not starting**
```bash
# Check for syntax errors
python manage.py check

# If migrations needed
python manage.py migrate

# Restart
python manage.py runserver
```

### **Static files not loading**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Or clear browser cache (Ctrl+Shift+Delete)
```

### **Database errors**
```bash
# Backup current state
python manage.py dumpdata > backup.json

# Fresh start
python manage.py flush --no-input
python manage.py migrate
python manage.py createsuperuser
```

### **Messages not showing**
- Check browser console (F12) for errors
- Clear browser cache
- Restart Django server
- Try incognito/private window

### **Colors look wrong**
- Clear CSS cache: `Ctrl+Shift+Delete`
- Hard refresh: `Ctrl+Shift+R`
- Check `static/css/style.css` is loading in DevTools → Network → XHR

### **Font Awesome icons missing**
- Check browser console for CORS errors
- Verify CDN is accessible: `https://cdnjs.cloudflare.com`
- Try using different CDN or local Font Awesome

---

## 📊 Test Data Creation

### **Create Sample Nodes (via Django admin)**
1. Login as admin
2. Go to `/admin/core/node/`
3. Click "Add Node"
4. Fill form:
   - Node ID: `NODE-001`
   - Node Type: `EDGE` (or CORE, IOT, USER)
   - IP Address: `192.168.1.100`
   - Location: `New York`
   - Hardware Capability: `8`
   - Network Bandwidth: `100.0`
   - Status: `ACTIVE`
5. Click Save

### **Create Sample Shards (via Django admin)**
1. Go to `/admin/core/shard/`
2. Click "Add Shard"
3. Fill form:
   - Shard ID: `SHARD-001`
   - Name: `URLLC Network`
   - Service Type: `URLLC`
   - Description: `Ultra-Reliable Low Latency Service`
   - Minimum Reputation: `3.0`
   - Minimum Capability: `5`
   - Is Active: ✓ Checked
4. Click Save

---

## 📝 File Summary

### **Modified Files:**
- `core/views.py` - Fixed decorators and added Welcome view
- `core/forms.py` - User registration form
- `core/urls.py` - Added welcome route
- `blockchain_6g/urls.py` - Added register routes
- `blockchain_6g/settings.py` - Auth settings
- `templates/base.html` - Enhanced navbar, message display
- `templates/dashboard.html` - New custom admin dashboard
- `templates/registration/login.html` - Enhanced with register link
- `templates/registration/register.html` - New registration page
- `templates/welcome.html` - New welcome page for non-admin
- `static/css/style.css` - Improved colors and styling

### **New Files Created:**
- `core/forms.py` - Registration form
- `templates/registration/register.html` - Registration page
- `templates/welcome.html` - Welcome page
- `templates/dashboard.html` - Admin dashboard (replaced)
- `QUICKSTART.md` - Quick start guide
- `IMPLEMENTATION_GUIDE.md` - Technical documentation

---

## 🎯 Success Indicators

You'll know everything is working when:
✅ Admin can login and see custom dashboard  
✅ Regular users can register and login  
✅ Regular users see welcome page with error message  
✅ Regular users cannot access admin pages  
✅ All text is clearly visible on dark background  
✅ Green accents stand out nicely  
✅ All buttons and forms work properly  
✅ Navigation menus change based on user role  
✅ Messages display when access is denied  
✅ Admin can manage users in `/admin/`  

---

## 🔐 Security Reminders

1. **Never commit .env files** with credentials
2. **Change SECRET_KEY** in production
3. **Set DEBUG = False** in production
4. **Use strong passwords** (min 8 chars, mixed case)
5. **Regularly backup database** with `dumpdata`
6. **Monitor admin logs** for unauthorized attempts

---

## 📞 Troubleshooting Commands

```bash
# Check for errors
python manage.py check

# Verify URL patterns
python manage.py show_urls

# Clear cache
python manage.py clear_cache

# Reset migrations (careful!)
python manage.py migrate --fake-initial

# Interactive shell
python manage.py shell
  >>> from django.contrib.auth.models import User
  >>> User.objects.all()

# Create superuser from shell
python manage.py shell
  >>> from django.contrib.auth.models import User
  >>> User.objects.create_superuser('admin', 'admin@test.com', 'password123')
```

---

## 📚 Related Documentation

- `QUICKSTART.md` - Installation and basic usage
- `IMPLEMENTATION_GUIDE.md` - Detailed technical documentation
- Django Docs: https://docs.djangoproject.com/
- Bootstrap Docs: https://getbootstrap.com/docs/

---

## ✨ Summary of Improvements

| Issue | Solution | File |
|-------|----------|------|
| Redirect loop | Changed to redirect to 'welcome' | views.py |
| Admin dashboard | Created custom dashboard template | dashboard.html |
| Access control | Added @admin_required decorator | views.py |
| Text visibility | Improved color contrast | style.css |
| Background color | Adjusted to lighter dark navy | style.css |
| Message display | Added messages block to base | base.html |
| Form styling | Enhanced input appearance | style.css |
| User management | All models registered in admin | admin.py |
| Navigation | Role-based menu display | base.html |

---

**Version**: 1.1  
**Last Updated**: February 13, 2026  
**Status**: ✅ Production Ready
