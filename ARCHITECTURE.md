# Teacher Assistant Platform - Architecture Documentation

## 📁 Project Structure

```
ta_project/
├── 📁 core/                          # Main Django application
│   ├── 📁 management/                # Django management commands
│   │   └── 📁 commands/
│   │       └── create_sample_data.py # Sample data generation
│   ├── 📁 migrations/                # Database migrations
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py                       # App configuration
│   ├── models.py                     # Database models
│   ├── serializers.py                # REST API serializers
│   ├── services.py                   # AI service layer
│   ├── tests.py                      # Unit tests
│   ├── urls.py                       # URL routing
│   └── views.py                      # View controllers
├── 📁 media/                         # User-uploaded files
│   ├── 📁 attempt_images/            # AI-generated corrected images
│   └── 📁 topic_images/              # AI-generated background images
├── 📁 static/                        # Static assets
│   ├── 📁 css/
│   │   └── style.css                 # Custom styles
│   └── 📁 js/                        # JavaScript files
├── 📁 ta_project/                    # Django project settings
│   ├── settings.py                   # Main configuration
│   ├── urls.py                       # Root URL configuration
│   ├── wsgi.py                       # WSGI configuration
│   └── asgi.py                       # ASGI configuration
├── 📁 templates/                     # HTML templates
│   ├── base.html                     # Base template
│   └── 📁 core/                      # App-specific templates
│       ├── admin_dashboard.html      # Admin dashboard
│       ├── create_group.html         # Group creation form
│       ├── create_topic.html         # Topic creation form
│       ├── create_user.html          # User creation form
│       ├── group_detail_admin.html   # Group progress view
│       ├── home.html                 # Student home page
│       └── topic_detail.html         # Interactive canvas page
├── .env                              # Environment variables
├── .gitignore                        # Git ignore rules
├── db.sqlite3                        # SQLite database
├── deploy.sh                         # Deployment script
├── manage.py                         # Django management script
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
└── ARCHITECTURE.md                   # This file
```

## 🏗️ System Architecture

### 1. Presentation Layer (Frontend)

#### HTML Templates
- **Base Template**: Common layout with navigation and styling
- **Student Interface**: Home page and interactive canvas
- **Admin Interface**: Management dashboards and forms

#### JavaScript Components
- **Canvas Drawing Engine**: HTML5 Canvas with drawing tools
- **AJAX Submission**: Asynchronous form submissions
- **Real-time Updates**: Dynamic content updates

#### CSS Framework
- **Bootstrap 5**: Responsive grid and components
- **Custom Styles**: Platform-specific styling
- **Mobile-First**: Responsive design principles

### 2. Application Layer (Django)

#### Models (Data Layer)
```python
Group           # Educational groups
├── members     # Many-to-many with Users
└── topics      # One-to-many with Topics

Topic           # Educational content
├── group       # Foreign key to Group
├── background_image    # AI-generated image
└── instructional_text  # AI-generated instructions

UserTopicProgress   # Progress tracking
├── user        # Foreign key to User
├── topic       # Foreign key to Topic
└── attempts    # One-to-many with Attempts

Attempt         # Individual submissions
├── user        # Foreign key to User
├── topic       # Foreign key to Topic
├── canvas_data # Base64 encoded PNG
├── score       # 0-20 evaluation score
└── feedback    # AI-generated feedback

AIGenerationLog # API call logging
├── generation_type  # image/text/evaluation
├── prompt      # Input prompt
├── response    # API response
└── success     # Success/failure flag
```

#### Views (Controller Layer)
```python
# Student Views
home()              # Display groups and topics
topic_detail()      # Interactive canvas page
submit_drawing()    # API endpoint for submissions

# Admin Views
admin_dashboard()   # Group overview
group_detail_admin() # Detailed progress view
create_user()       # User creation form
create_group()      # Group creation form
create_topic()      # Topic creation with AI generation
```

#### Services (Business Logic)
```python
AIService
├── generate_image()     # Image generation API
├── generate_text()      # Text generation API
└── evaluate_drawing()   # Drawing evaluation API

TopicContentGenerator
└── generate_topic_content()  # Complete topic setup

FeedbackGenerator
└── generate_corrected_content()  # Error correction
```

### 3. Integration Layer (AI Services)

#### Image Generation Pipeline
```
Topic Creation → AI Prompt → Image API → Background Image
     ↓
Error Detection → Correction Prompt → Image API → Updated Image
```

#### Text Generation Pipeline
```
Topic Creation → AI Prompt → Text API → Instructions
     ↓
Student Error → Feedback Prompt → Text API → Guidance
```

#### Evaluation Pipeline
```
Canvas Submission → AI Analysis → Score + Feedback
     ↓
Error Detection → Content Update → New Instructions
```

### 4. Data Layer (Database)

#### Entity Relationships
```
User ←→ Group (Many-to-Many)
Group → Topic (One-to-Many)
User + Topic → Progress (One-to-One)
User + Topic → Attempt (One-to-Many)
Topic/Attempt → AIGenerationLog (One-to-Many)
```

#### Data Flow
```
1. Admin creates Topic with prompt
2. AI generates background image + instructions
3. Student accesses Topic
4. Student draws on canvas
5. Canvas data submitted to API
6. AI evaluates submission
7. Feedback generated and stored
8. Progress updated
```

## 🔄 Request Flow

### Student Workflow
```
1. Login → Authentication Check
2. Home Page → Load User Groups + Topics
3. Topic Selection → Check Access Permissions
4. Canvas Loading → Display Background + Instructions
5. Drawing Interaction → Client-side Canvas API
6. Submission → AJAX POST to API
7. AI Evaluation → Background Processing
8. Results Display → Update UI with Feedback
```

### Admin Workflow
```
1. Login → Admin Permission Check
2. Dashboard → Load All Groups + Statistics
3. Topic Creation → Form Submission
4. AI Content Generation → Background API Calls
5. Content Storage → Database + Media Files
6. Progress Monitoring → Real-time Analytics
```

## 🔧 Technical Decisions

### Framework Choice: Django
- **Pros**: Rapid development, built-in admin, ORM, security
- **Cons**: Monolithic structure, Python performance
- **Alternatives**: FastAPI, Flask, Node.js

### Database: SQLite (Development) / PostgreSQL (Production)
- **Pros**: Simple setup, ACID compliance, JSON support
- **Cons**: Concurrent write limitations (SQLite)
- **Alternatives**: MySQL, MongoDB

### Frontend: Server-side Templates + JavaScript
- **Pros**: SEO-friendly, simple deployment, progressive enhancement
- **Cons**: Limited interactivity, page reloads
- **Alternatives**: React SPA, Vue.js, Angular

### AI Integration: REST APIs
- **Pros**: Provider flexibility, caching, error handling
- **Cons**: Network latency, API costs
- **Alternatives**: Local models, GraphQL

## 🚀 Scalability Considerations

### Performance Bottlenecks
1. **AI API Calls**: Rate limiting, caching, async processing
2. **Canvas Data**: Large base64 images, compression
3. **Database Queries**: N+1 problems, indexing
4. **Static Files**: CDN, compression, caching

### Scaling Solutions
```
Load Balancer
├── Web Server 1 (Django)
├── Web Server 2 (Django)
└── Web Server N (Django)
     ↓
Database Cluster
├── Primary (Write)
└── Replicas (Read)
     ↓
External Services
├── Redis (Caching)
├── Celery (Background Tasks)
└── CDN (Static Files)
```

### Horizontal Scaling
- **Stateless Design**: No server-side sessions
- **Database Sharding**: Partition by group/user
- **Microservices**: Separate AI service
- **Caching Strategy**: Redis for frequent data

## 🔒 Security Architecture

### Authentication & Authorization
```
User Authentication
├── Django Sessions
├── CSRF Protection
└── Permission Decorators

API Security
├── CSRF Tokens
├── Rate Limiting
└── Input Validation

Data Protection
├── SQL Injection Prevention (ORM)
├── XSS Protection (Template Escaping)
└── File Upload Validation
```

### AI API Security
- **API Key Management**: Environment variables
- **Request Validation**: Input sanitization
- **Response Filtering**: Content moderation
- **Usage Monitoring**: Cost and rate tracking

## 📊 Monitoring & Observability

### Application Metrics
- **User Engagement**: Login frequency, session duration
- **Learning Progress**: Completion rates, attempt patterns
- **System Performance**: Response times, error rates

### AI Service Metrics
- **API Usage**: Request count, cost tracking
- **Generation Quality**: Success rates, error types
- **Evaluation Accuracy**: Score distributions, feedback quality

### Infrastructure Metrics
- **Server Resources**: CPU, memory, disk usage
- **Database Performance**: Query times, connection pools
- **Network**: Bandwidth, latency, availability

## 🔮 Future Architecture

### Microservices Migration
```
API Gateway
├── User Service (Authentication)
├── Content Service (Groups/Topics)
├── Canvas Service (Drawing/Submission)
├── AI Service (Generation/Evaluation)
└── Analytics Service (Progress/Reporting)
```

### Event-Driven Architecture
```
Event Bus (Apache Kafka)
├── User Events (Login, Progress)
├── Content Events (Creation, Updates)
├── Submission Events (Canvas, Evaluation)
└── AI Events (Generation, Completion)
```

### Cloud-Native Deployment
```
Kubernetes Cluster
├── Web Pods (Django)
├── Worker Pods (Celery)
├── Database (Managed Service)
├── Cache (Redis)
└── Storage (Object Storage)
```

This architecture provides a solid foundation for the Teacher Assistant platform while maintaining flexibility for future enhancements and scaling requirements.