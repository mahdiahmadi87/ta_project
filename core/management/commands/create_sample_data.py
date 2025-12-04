from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Group, Topic, UserTopicProgress, Attempt
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Create sample data for testing the TA platform'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        users_data = [
            {'username': 'student1', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@example.com'},
            {'username': 'student2', 'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob@example.com'},
            {'username': 'student3', 'first_name': 'Carol', 'last_name': 'Davis', 'email': 'carol@example.com'},
            {'username': 'student4', 'first_name': 'David', 'last_name': 'Wilson', 'email': 'david@example.com'},
            {'username': 'teacher1', 'first_name': 'Dr. Sarah', 'last_name': 'Brown', 'email': 'sarah@example.com'},
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'is_staff': user_data['username'].startswith('teacher')
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            created_users.append(user)
        
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = created_users[0]
        
        # Create sample groups
        groups_data = [
            {
                'name': 'Physics 101',
                'description': 'Introduction to Physics - Forces and Motion',
                'members': created_users[:3]  # First 3 students
            },
            {
                'name': 'Chemistry Basics',
                'description': 'Basic Chemistry - Molecular Structure and Bonding',
                'members': created_users[1:4]  # Students 2-4
            },
            {
                'name': 'Mathematics Advanced',
                'description': 'Advanced Mathematics - Geometry and Calculus',
                'members': [created_users[0], created_users[2], created_users[3]]  # Students 1, 3, 4
            }
        ]
        
        created_groups = []
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name'],
                defaults={
                    'description': group_data['description'],
                    'created_by': admin_user
                }
            )
            if created:
                group.members.set(group_data['members'])
                self.stdout.write(f'Created group: {group.name}')
            created_groups.append(group)
        
        # Create sample topics
        topics_data = [
            {
                'title': 'Forces on Inclined Plane',
                'description': 'Learn to identify and draw force vectors on objects on inclined planes.',
                'prompt': 'Create a physics diagram showing a block on a 30-degree inclined plane. Students should draw: 1) gravitational force (red arrow pointing down), 2) normal force (blue arrow perpendicular to surface), 3) friction force (green arrow opposing motion). Include proper vector directions and magnitudes.',
                'group': created_groups[0],  # Physics 101
                'instructional_text': '''Welcome to the Forces on Inclined Plane exercise!

Your task is to draw the three main forces acting on the block:

1. **Gravitational Force (Red)**: Draw a red arrow pointing straight down from the center of the block. This represents the weight of the object.

2. **Normal Force (Blue)**: Draw a blue arrow pointing perpendicular to the inclined surface, away from the plane. This force prevents the block from sinking into the surface.

3. **Friction Force (Green)**: Draw a green arrow pointing up the incline, opposing the motion. This force resists the sliding motion.

Remember:
- Use the correct colors for each force
- Make sure the directions are accurate
- The normal force should be perpendicular to the surface
- The friction force should oppose motion

Good luck!'''
            },
            {
                'title': 'Water Molecule Structure',
                'description': 'Draw the molecular structure of water (H2O) showing bonds and electron pairs.',
                'prompt': 'Create a molecular diagram template for water (H2O). Show oxygen atom in the center with spaces for students to draw hydrogen atoms and electron pairs. Students should draw: 1) two hydrogen atoms (small circles), 2) two lone pairs of electrons (dots), 3) covalent bonds (lines). Include angle measurements.',
                'group': created_groups[1],  # Chemistry Basics
                'instructional_text': '''Welcome to the Water Molecule Structure exercise!

Your task is to complete the water molecule diagram:

1. **Hydrogen Atoms**: Draw two small circles representing hydrogen atoms. Position them at approximately 104.5° angle from each other.

2. **Covalent Bonds**: Draw straight lines connecting each hydrogen atom to the central oxygen atom. These represent shared electron pairs.

3. **Lone Pairs**: Draw two pairs of dots on the oxygen atom representing the two lone pairs of electrons that are not involved in bonding.

4. **Molecular Geometry**: The molecule should have a bent shape due to the lone pairs pushing the hydrogen atoms closer together.

Remember:
- The bond angle is approximately 104.5°
- Oxygen is more electronegative than hydrogen
- The molecule is polar due to the bent shape

Complete the diagram step by step!'''
            },
            {
                'title': 'Triangle Centroid',
                'description': 'Find and draw the centroid of a triangle using medians.',
                'prompt': 'Create a coordinate plane with triangle ABC where A(2,3), B(6,3), C(4,7). Students need to: 1) draw and label the triangle vertices, 2) calculate and draw the centroid (red dot), 3) draw the three medians (dashed lines), 4) label all measurements. Include grid lines and axis labels.',
                'group': created_groups[2],  # Mathematics Advanced
                'instructional_text': '''Welcome to the Triangle Centroid exercise!

Your task is to find and draw the centroid of triangle ABC:

Given vertices:
- A(2, 3)
- B(6, 3)  
- C(4, 7)

Steps to complete:

1. **Draw the Triangle**: Connect the three vertices to form triangle ABC.

2. **Find Midpoints**: Calculate the midpoint of each side:
   - Midpoint of AB: ((2+6)/2, (3+3)/2) = (4, 3)
   - Midpoint of BC: ((6+4)/2, (3+7)/2) = (5, 5)
   - Midpoint of AC: ((2+4)/2, (3+7)/2) = (3, 5)

3. **Draw Medians**: Draw dashed lines from each vertex to the opposite side's midpoint.

4. **Mark Centroid**: The centroid is at ((2+6+4)/3, (3+3+7)/3) = (4, 4.33). Mark this with a red dot.

The centroid divides each median in a 2:1 ratio!'''
            }
        ]
        
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                title=topic_data['title'],
                group=topic_data['group'],
                defaults={
                    'description': topic_data['description'],
                    'prompt': topic_data['prompt'],
                    'instructional_text': topic_data['instructional_text'],
                    'created_by': admin_user,
                    'content_generated': True  # Mark as generated for demo
                }
            )
            if created:
                self.stdout.write(f'Created topic: {topic.title}')
        
        # Create some sample progress and attempts
        topics = Topic.objects.all()
        students = [u for u in created_users if not u.is_staff and not u.is_superuser]
        
        for topic in topics:
            for student in topic.group.members.all():
                if student in students:
                    # Create progress
                    progress, created = UserTopicProgress.objects.get_or_create(
                        user=student,
                        topic=topic,
                        defaults={
                            'total_attempts': random.randint(1, 3),
                            'total_time_spent': random.randint(300, 1800),  # 5-30 minutes
                            'first_attempt_at': timezone.now() - timezone.timedelta(days=random.randint(1, 7))
                        }
                    )
                    
                    if created:
                        # Maybe complete some topics
                        if random.random() < 0.3:  # 30% chance of completion
                            progress.completed = True
                            progress.final_score = random.randint(15, 20)
                            progress.completed_at = timezone.now() - timezone.timedelta(days=random.randint(0, 3))
                            progress.save()
                        
                        # Create some attempts
                        for attempt_num in range(1, progress.total_attempts + 1):
                            Attempt.objects.get_or_create(
                                user=student,
                                topic=topic,
                                attempt_number=attempt_num,
                                defaults={
                                    'canvas_data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',  # 1x1 transparent PNG
                                    'score': random.randint(8, 20),
                                    'is_correct': progress.completed and attempt_num == progress.total_attempts,
                                    'feedback': 'Sample feedback for demonstration purposes.',
                                    'time_spent': random.randint(60, 600),  # 1-10 minutes
                                    'started_at': timezone.now() - timezone.timedelta(days=random.randint(1, 7)),
                                    'evaluation_completed': True
                                }
                            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('Login credentials:')
        self.stdout.write('- Admin: admin / (your password)')
        self.stdout.write('- Students: student1-4 / password123')
        self.stdout.write('- Teacher: teacher1 / password123')