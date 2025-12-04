#!/bin/bash

# Teacher Assistant Platform Deployment Script

echo "🚀 Starting Teacher Assistant Platform Deployment..."

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env 2>/dev/null || echo "Please create .env file with your API keys"
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one:')
    exit(1)
else:
    print('Superuser already exists.')
" || {
    echo "Creating superuser..."
    python manage.py createsuperuser
}

# Create sample data (optional)
read -p "📊 Do you want to create sample data for testing? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎯 Creating sample data..."
    python manage.py create_sample_data
fi

# Run tests
echo "🧪 Running tests..."
python manage.py test core

# Start development server
echo "🌟 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your AI API keys in .env file"
echo "2. Start the server with: python manage.py runserver"
echo "3. Access the platform at: http://127.0.0.1:8000"
echo ""
echo "👥 Default login credentials (if sample data was created):"
echo "   Admin: admin / (your password)"
echo "   Students: student1-4 / password123"
echo "   Teacher: teacher1 / password123"
echo ""

read -p "🚀 Start development server now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting server..."
    python manage.py runserver
fi