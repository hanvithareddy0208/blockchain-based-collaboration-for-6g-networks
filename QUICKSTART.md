# 6G Blockchain System - Quick Start Guide

## Prerequisites

- Python 3.8+
- MySQL 5.7+ or MariaDB
- Django 4.2.7
- All dependencies from requirements.txt

---

## Installation Steps

### 1. Activate Virtual Environment

```bash
# Windows
bl6genv\Scripts\activate

# Linux/Mac
source bl6genv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account:
- Username: `admin` or your preferred username
- Email: `admin@example.com` (your email)
- Password: (choose a strong password)
- Confirm password: (repeat the password)

### 5. Run Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000`

---

## Access the Application

### For Admin Users:
1. Navigate to `http://localhost:8000`
2. You'll be redirected to the login page
3. Login with your superuser credentials
4. You'll have access to the full dashboard and all management pages
5. Visit `http://localhost:8000/admin/` to access the admin panel

### For Regular Users:
1. Navigate to `http://localhost:8000/register/`
2. Fill in the registration form:
   - Username (required)
   - Email (required - must be unique)
   - First Name (optional)
   - Last Name (optional)
   - Password (required - must be at least 8 characters)
   - Confirm Password (required - must match)
3. Click "Create Account"
4. You'll be redirected to the login page
5. Login with your credentials
6. You'll see a welcome page with account details
7. Contact an admin to request elevated privileges

---

## Key Features

### 1. Multi-User Support
✓ Register new users
✓ Secure password storage
✓ Email validation (unique)
✓ Username validation (unique)

### 2. Admin Dashboard (Admin Only)
✓ View all blockchain data
✓ Manage nodes, shards, transactions
✓ Monitor consensus rounds
✓ View storage records
✓ Track reputation history

### 3. Admin Panel (Admin Only)
✓ Complete user management
✓ View all registered users
✓ Grant/revoke admin privileges
✓ Manage all blockchain models
✓ Advanced filtering and search

### 4. Role-Based Access Control
✓ Admin users: Full access to dashboard and admin panel
✓ Regular users: Welcome page with account info
✓ Unauthenticated users: Restricted to login/register pages

### 5. Modern UI
✓ Black & Green theme
✓ Responsive design (mobile-friendly)
✓ Clear visibility (white text on black)
✓ Font Awesome icons
✓ Bootstrap 5 styling

---

## Common Tasks

### Creating a User Account

**Via Registration Page:**
1. Click "Register" or navigate to `/register/`
2. Fill in all required fields
3. Click "Create Account"
4. Login with the new credentials

**Via Admin Panel (Admin Only):**
1. Login to `http://localhost:8000/admin/`
2. Click "Users" in the left sidebar
3. Click "Add User"
4. Fill in username and password
5. Click "Save and continue editing"
6. Add email, first name, last name
7. To make user an admin: Check "Staff status" or "Superuser status"
8. Click "Save"

### Granting Admin Privileges

1. Login as superuser to admin panel (`/admin/`)
2. Click "Users" in the sidebar
3. Select the user to upgrade
4. Check the "Staff status" checkbox (or "Superuser status" for full admin)
5. Click "Save"
6. The user must logout and login again for changes to take effect

### Viewing System Data

**As Admin:**
1. Login to dashboard
2. Navigate to desired section:
   - Dashboard: Overview and statistics
   - Nodes: Network node management
   - Shards: Shard management
   - Transactions: Transaction monitoring
   - Consensus: Consensus monitoring
   - Storage: Storage management

**As Admin Panel User:**
1. Navigate to `/admin/`
2. Select any model to view/edit/delete data
3. Use filters and search for specific records

### Managing User Accounts (Admin Only)

1. Navigate to `/admin/`
2. Click "Users"
3. Options:
   - **Change User**: Click username to edit
   - **View Permissions**: Check staff, superuser, active status
   - **View Login Info**: See last login, date joined
   - **Delete User**: Select and use "Delete selected users" action

---

## Troubleshooting

### Issue: "Database connection refused"
**Solution:**
- Ensure MySQL is running
- Check database credentials in settings.py or .env file
- Verify DB_HOST, DB_USER, DB_PASSWORD are correct

### Issue: "Page not found (404)"
**Solution:**
- Ensure you're using the correct URL
- Check that Django development server is running
- Clear browser cache (Ctrl+F5)

### Issue: "No module named 'core'"
**Solution:**
- Ensure you're in the correct project directory
- Activate the virtual environment
- Run `python manage.py` from the same directory as manage.py

### Issue: "CSRF verification failed"
**Solution:**
- Ensure cookies are enabled in your browser
- Clear browser cookies and cache
- Restart Django development server

### Issue: "You don't have permission to access this page"
**Solution:**
- You're likely logged in as non-admin user trying to access admin page
- Either login as admin user, or request admin privileges
- Admin can grant privileges in /admin/ → Users

### Issue: "Email already registered"
**Solution:**
- The email is already in use by another account
- Use a different email address or reset the password for the existing account

---

## Port Configuration

By default, the development server runs on port 8000. To use a different port:

```bash
python manage.py runserver 0.0.0.0:8080
```

Available at: `http://localhost:8080`

---

## Static Files

For development, static files are served automatically.

For production:
```bash
python manage.py collectstatic
```

---

## Database Backup & Restore

### Backup Data:
```bash
python manage.py dumpdata > backup.json
```

### Restore Data:
```bash
python manage.py loaddata backup.json
```

---

## Useful Django Commands

```bash
# Create migrations for model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Enter Django shell
python manage.py shell

# View URL patterns
python manage.py show_urls

# Check system status
python manage.py check
```

---

## Environment Configuration

Create a `.env` file in the project root to override default database settings:

```
DB_NAME=6g_blockchain
DB_USER=root
DB_PASSWORD=YourPassword
DB_HOST=localhost
DB_PORT=3306
```

---

## Browser Compatibility

- Chrome/Brave: Full support
- Firefox: Full support
- Edge: Full support
- Safari: Full support
- Mobile browsers: Responsive design supported

---

## Support Files

- **IMPLEMENTATION_GUIDE.md**: Detailed technical documentation
- **requirements.txt**: Python dependencies
- **manage.py**: Django management script
- **settings.py**: Django configuration

---

## What's Next?

1. ✅ Install and run the server
2. ✅ Create a superuser account
3. ✅ Register some test users
4. ✅ Explore the admin dashboard
5. ✅ Create test blockchain data (nodes, shards, transactions)
6. ✅ Test access control restrictions
7. ✅ Deploy to production when ready

---

## Need Help?

- Check IMPLEMENTATION_GUIDE.md for detailed technical info
- Review error messages in Django console
- Check Django documentation: https://docs.djangoproject.com/
- Review code comments in views.py, models.py, admin.py

---

**Version**: 1.0  
**Last Updated**: February 13, 2026
