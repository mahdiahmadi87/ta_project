# Teacher Assistant (TA) Platform

A comprehensive Django-based interactive educational system where users join groups, view assigned topics, and complete interactive tasks by drawing directly on a canvas. The platform uses AI to generate content and evaluate student submissions.

## 🚀 Features

### Core Functionality
- **Interactive Canvas Drawing**: Students can draw, erase, add text, and use multiple colors
- **AI-Powered Content Generation**: Automatic generation of background images and instructional text
- **Real-time Evaluation**: AI evaluates student drawings and provides detailed feedback
- **Progress Tracking**: Complete attempt history and scoring system
- **Group Management**: Organize students into groups with assigned topics

### AI Integration
- **Image Generation**: Creates educational diagrams and backgrounds using AI
- **Text Generation**: Generates step-by-step instructional content
- **Drawing Evaluation**: AI analyzes student submissions and provides feedback
- **Adaptive Learning**: Updates content based on student mistakes

### Admin Features
- Create and manage users, groups, and topics
- Monitor student progress across all groups
- View detailed attempt histories and scores
- Generate AI-powered educational content

## 🏗️ Architecture

### Backend (Django)
- **Models**: User management, groups, topics, progress tracking, attempts
- **Views**: Web pages and REST API endpoints
- **Services**: AI integration layer for image/text generation and evaluation
- **Admin**: Comprehensive admin interface for content management

### Frontend (JavaScript + Bootstrap)
- **Interactive Canvas**: HTML5 Canvas with drawing tools
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Dynamic content updates based on AI feedback

### AI Services
- **Image Generation API**: Creates educational diagrams and backgrounds
- **Text Generation API**: Produces instructional content and feedback
- **Evaluation Engine**: Analyzes student drawings and provides scores

## 📋 Requirements

- Python 3.10+
- Django 5.2.9
- Django REST Framework
- PIL (Pillow) for image processing
- Requests for API calls
- AI API keys (OpenAI or compatible)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ta_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create sample data (optional)**
   ```bash
   python manage.py create_sample_data
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# AI API Configuration
IMAGE_GENERATION_API_KEY=your_image_generation_api_key_here
TEXT_GENERATION_API_KEY=your_text_generation_api_key_here

# Image Generation API Settings
IMAGE_API_URL=https://api.openai.com/v1/images/generations
IMAGE_MODEL=dall-e-3

# Text Generation API Settings  
TEXT_API_URL=https://api.openai.com/v1/chat/completions
TEXT_MODEL=gpt-4

# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### AI API Setup
The platform supports OpenAI APIs by default but can be configured for other providers:

1. **OpenAI Setup**:
   - Get API key from https://platform.openai.com/
   - Set `IMAGE_GENERATION_API_KEY` and `TEXT_GENERATION_API_KEY`

2. **Custom API Setup**:
   - Update `IMAGE_API_URL` and `TEXT_API_URL` in settings
   - Modify `core/services.py` if different request format needed

## 📚 Usage

### For Students
1. **Login**: Use provided credentials to access the platform
2. **Browse Topics**: View assigned topics in your groups
3. **Interactive Learning**: 
   - Open a topic to see the canvas and instructions
   - Use drawing tools to complete the exercise
   - Submit your work for AI evaluation
4. **Track Progress**: View your attempt history and scores

### For Administrators
1. **Access Admin Panel**: Use admin credentials to access management features
2. **Create Users**: Add new students and teachers
3. **Manage Groups**: Create groups and assign members
4. **Create Topics**: 
   - Define educational topics with AI prompts
   - AI automatically generates background images and instructions
5. **Monitor Progress**: View detailed analytics for all students

### Canvas Tools
- **Draw**: Freehand drawing with adjustable brush size
- **Erase**: Remove parts of your drawing
- **Text**: Add text labels to your drawing
- **Colors**: Choose from 8 different colors
- **Clear**: Start over with a blank canvas

## 🎯 Educational Use Cases

### Physics
```
Topic: Forces on Inclined Plane
Prompt: Create a physics diagram showing a block on a 30-degree inclined plane. 
Students should draw: 1) gravitational force (red arrow pointing down), 
2) normal force (blue arrow perpendicular to surface), 3) friction force 
(green arrow opposing motion).
```

### Chemistry
```
Topic: Water Molecule Structure
Prompt: Create a molecular diagram template for water (H2O). Show oxygen atom 
in the center with spaces for students to draw hydrogen atoms and electron pairs. 
Students should draw: 1) two hydrogen atoms, 2) two lone pairs of electrons, 
3) covalent bonds.
```

### Mathematics
```
Topic: Triangle Centroid
Prompt: Create a coordinate plane with triangle ABC where A(2,3), B(6,3), C(4,7). 
Students need to: 1) draw and label the triangle vertices, 2) calculate and draw 
the centroid, 3) draw the three medians, 4) label all measurements.
```

## 🔧 API Endpoints

### Student APIs
- `GET /` - Home page with groups and topics
- `GET /topic/<id>/` - Topic detail with interactive canvas
- `POST /api/topic/<id>/submit/` - Submit canvas drawing for evaluation

### Admin APIs
- `GET /dashboard/` - Admin dashboard
- `GET /dashboard/group/<id>/` - Detailed group progress
- `POST /dashboard/create-user/` - Create new user
- `POST /dashboard/create-group/` - Create new group
- `POST /dashboard/create-topic/` - Create new topic with AI content

## 📊 Database Schema

### Core Models
- **Group**: Educational groups containing users and topics
- **Topic**: Educational topics with AI-generated content
- **UserTopicProgress**: Tracks user progress on topics
- **Attempt**: Individual submission attempts with scores and feedback
- **AIGenerationLog**: Logs all AI API calls for monitoring

### Key Relationships
- Users belong to multiple Groups (many-to-many)
- Topics belong to one Group (foreign key)
- Progress tracks User-Topic pairs (unique together)
- Attempts link Users to Topics with attempt numbers

## 🧪 Testing

Run the test suite:
```bash
python manage.py test core
```

The tests cover:
- User authentication and authorization
- Group and topic management
- Canvas submission workflow
- Progress tracking
- Admin functionality

## 🚀 Deployment

### Production Checklist
1. **Security**:
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Use HTTPS for API calls

2. **Database**:
   - Use PostgreSQL or MySQL for production
   - Set up database backups
   - Configure connection pooling

3. **Static Files**:
   - Configure static file serving (nginx/Apache)
   - Set up CDN for media files
   - Optimize images and CSS

4. **AI APIs**:
   - Monitor API usage and costs
   - Implement rate limiting
   - Set up error handling and retries

### Docker Deployment
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🔍 Monitoring

### AI Generation Logs
The platform logs all AI API calls in the `AIGenerationLog` model:
- Track API usage and costs
- Monitor success/failure rates
- Debug generation issues

### Performance Metrics
- Canvas submission response times
- AI evaluation accuracy
- User engagement metrics
- System resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**AI Content Not Generating**:
- Check API keys in `.env` file
- Verify API endpoints are accessible
- Check `AIGenerationLog` for error messages

**Canvas Not Working**:
- Ensure JavaScript is enabled
- Check browser console for errors
- Verify CSRF tokens are present

**Permission Denied**:
- Check user group memberships
- Verify admin permissions
- Review URL patterns

### Getting Help
- Check the Django admin panel for detailed error logs
- Review the `AIGenerationLog` model for API issues
- Use browser developer tools for frontend debugging

## 🔮 Future Enhancements

- **Real-time Collaboration**: Multiple students working on the same canvas
- **Voice Instructions**: Audio guidance for accessibility
- **Mobile App**: Native mobile applications
- **Advanced Analytics**: Machine learning insights on learning patterns
- **Gamification**: Points, badges, and leaderboards
- **Video Integration**: Record drawing sessions for review

---

**Built with ❤️ using Django, JavaScript, and AI**