#!/usr/bin/env python3
import os
import sys
import django
import secrets
import itertools

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
django_project_path = os.path.join(project_root, 'django-lms')

if os.path.exists(django_project_path):
    sys.path.insert(0, django_project_path)
    print(f"Using Django project path: {django_project_path}")
else:
    fallback_path = '/opt/lab/django-lms'
    if os.path.exists(fallback_path):
        sys.path.insert(0, fallback_path)
        print(f"Using fallback Django project path: {fallback_path}")
    else:
        print(f"ERROR: Django project not found!")
        print(f"  Tried: {django_project_path}")
        print(f"  Tried: {fallback_path}")
        sys.exit(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_portal.settings')

try:
    django.setup()
except Exception as e:
    print(f"ERROR: Failed to setup Django: {e}")
    print(f"  DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"  Python path: {sys.path}")
    sys.exit(1)

from django.contrib.auth.models import User
from courses.models import Course, UserProfile, Enrollment

def load_env_file(path):
    data = {}
    if not path or not os.path.exists(path):
        return data
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                data[key.strip()] = value.strip()
    except OSError:
        return data
    return data

def create_superuser():
    username = 'admin'
    email = 'admin@lms.local'

    password = os.environ.get('DJANGO_ADMIN_PASSWORD')
    if not password:
        root_env = load_env_file('/root/lab_credentials.env')
        password = root_env.get('DJANGO_ADMIN_PASSWORD')
    if not password:
        fallback_env = load_env_file(os.path.join(project_root, 'config', 'credentials.env'))
        password = fallback_env.get('DJANGO_ADMIN_PASSWORD')
    if not password:
        password = secrets.token_urlsafe(16)
    
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
    else:
        user = User.objects.create_superuser(username, email, password)
        print(f"Created superuser: {username}")
    
    return user

def create_test_users():
    users_data = [
        {'username': 'student1', 'email': 'student1@lms.local', 'password': 'student123'},
        {'username': 'student2', 'email': 'student2@lms.local', 'password': 'student123'},
        {'username': 'teacher1', 'email': 'teacher1@lms.local', 'password': 'teacher123'},
    ]
    
    users = []
    for user_data in users_data:
        if User.objects.filter(username=user_data['username']).exists():
            user = User.objects.get(username=user_data['username'])
            user.set_password(user_data['password'])
            user.save()
            print(f"Updated user: {user_data['username']}")
        else:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            print(f"Created user: {user_data['username']}")
        users.append(user)
    
    return users

def create_user_profiles(users):
    profiles = []
    for user in users:
        api_key = f"api_{secrets.token_hex(16)}"
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'api_key': api_key}
        )
        if not created:
            profile.api_key = api_key
            profile.save()
        print(f"Profile for {user.username} created")
        profiles.append(profile)
    return profiles

def create_courses(profiles, admin_profile):
    profiles = profiles or []
    non_admin_profiles = [profile for profile in profiles if profile != admin_profile]
    profile_cycle = itertools.cycle(non_admin_profiles) if non_admin_profiles else None
    courses_data = [
        {
            'title': 'Python Programming Basics',
            'category': 'Programming',
            'level': 'beginner',
            'description': 'Learn the fundamentals of Python programming language. Perfect for beginners. Cover variables, data types, control structures, functions, and basic object-oriented programming concepts.',
            'is_hidden': False
        },
        {
            'title': 'JavaScript for Beginners',
            'category': 'Programming',
            'level': 'beginner',
            'description': 'Start your journey with JavaScript programming. Learn syntax, DOM manipulation, events, and basic web development concepts.',
            'is_hidden': False
        },
        {
            'title': 'Java Fundamentals',
            'category': 'Programming',
            'level': 'beginner',
            'description': 'Introduction to Java programming language. Learn object-oriented programming, classes, inheritance, and basic Java syntax.',
            'is_hidden': False
        },
        {
            'title': 'C++ Programming Basics',
            'category': 'Programming',
            'level': 'beginner',
            'description': 'Master the fundamentals of C++ programming. Cover pointers, memory management, and object-oriented concepts.',
            'is_hidden': False
        },
        {
            'title': 'HTML & CSS Fundamentals',
            'category': 'Web Development',
            'level': 'beginner',
            'description': 'Learn the building blocks of web development. Master HTML structure and CSS styling to create beautiful web pages.',
            'is_hidden': False
        },
        {
            'title': 'Data Structures and Algorithms',
            'category': 'Programming',
            'level': 'intermediate',
            'description': 'Deep dive into data structures like arrays, linked lists, trees, and graphs. Learn algorithm design and complexity analysis.',
            'is_hidden': False
        },
        {
            'title': 'Object-Oriented Design Patterns',
            'category': 'Programming',
            'level': 'intermediate',
            'description': 'Learn common design patterns including Singleton, Factory, Observer, and Strategy patterns. Apply best practices in software design.',
            'is_hidden': False
        },
        {
            'title': 'RESTful API Development',
            'category': 'Programming',
            'level': 'intermediate',
            'description': 'Build RESTful APIs using best practices. Learn HTTP methods, status codes, authentication, and API documentation.',
            'is_hidden': False
        },
        {
            'title': 'Git Version Control',
            'category': 'Programming',
            'level': 'intermediate',
            'description': 'Master Git for version control. Learn branching, merging, pull requests, and collaborative development workflows.',
            'is_hidden': False
        },
        {
            'title': 'Advanced Django Development',
            'category': 'Web Development',
            'level': 'advanced',
            'description': 'Master Django framework for building complex web applications. Learn advanced ORM, middleware, caching, and deployment strategies.',
            'is_hidden': False
        },
        {
            'title': 'Secret API Development',
            'category': 'Programming',
            'level': 'advanced',
            'description': 'Advanced API development techniques including microservices, GraphQL, WebSockets, and API security. Restricted access.',
            'is_hidden': True
        },
        {
            'title': 'System Design and Architecture',
            'category': 'Programming',
            'level': 'advanced',
            'description': 'Learn to design scalable systems. Cover load balancing, caching strategies, database sharding, and distributed systems.',
            'is_hidden': False
        },
        {
            'title': 'Machine Learning with Python',
            'category': 'Programming',
            'level': 'advanced',
            'description': 'Introduction to machine learning using Python. Learn scikit-learn, neural networks, and model evaluation techniques.',
            'is_hidden': False
        },
        {
            'title': 'React Server Components',
            'category': 'Web Development',
            'level': 'intermediate',
            'description': 'Learn about React Server Components and their implementation. Understand server-side rendering and modern React patterns.',
            'is_hidden': False
        },
        {
            'title': 'Vue.js Complete Guide',
            'category': 'Web Development',
            'level': 'intermediate',
            'description': 'Comprehensive guide to Vue.js framework. Learn components, routing, state management with Vuex, and building SPAs.',
            'is_hidden': False
        },
        {
            'title': 'Node.js Backend Development',
            'category': 'Web Development',
            'level': 'intermediate',
            'description': 'Build scalable backend applications with Node.js. Learn Express.js, database integration, authentication, and API development.',
            'is_hidden': False
        },
        {
            'title': 'Full-Stack Web Development',
            'category': 'Web Development',
            'level': 'advanced',
            'description': 'Complete full-stack development course covering frontend, backend, databases, and deployment. Build real-world applications.',
            'is_hidden': False
        },
        {
            'title': 'Progressive Web Apps (PWA)',
            'category': 'Web Development',
            'level': 'intermediate',
            'description': 'Learn to build Progressive Web Apps that work offline, load fast, and provide native app-like experiences.',
            'is_hidden': False
        },
        {
            'title': 'Cybersecurity Fundamentals',
            'category': 'Security',
            'level': 'intermediate',
            'description': 'Introduction to cybersecurity concepts and best practices. Learn about threats, vulnerabilities, and security controls.',
            'is_hidden': False
        },
        {
            'title': 'Database Security',
            'category': 'Security',
            'level': 'advanced',
            'description': 'Advanced database security and SQL injection prevention. Learn secure coding practices, encryption, and access control.',
            'is_hidden': False
        },
        {
            'title': 'Web Application Security',
            'category': 'Security',
            'level': 'intermediate',
            'description': 'Learn to secure web applications against common vulnerabilities like XSS, CSRF, SQL injection, and authentication flaws.',
            'is_hidden': False
        },
        {
            'title': 'Penetration Testing Basics',
            'category': 'Security',
            'level': 'advanced',
            'description': 'Introduction to ethical hacking and penetration testing. Learn tools and techniques for security assessment.',
            'is_hidden': False
        },
        {
            'title': 'Cryptography Essentials',
            'category': 'Security',
            'level': 'intermediate',
            'description': 'Understand cryptographic principles, encryption algorithms, digital signatures, and secure communication protocols.',
            'is_hidden': False
        },
        {
            'title': 'SQL Mastery',
            'category': 'Database',
            'level': 'intermediate',
            'description': 'Master SQL for database management. Learn complex queries, joins, subqueries, stored procedures, and optimization.',
            'is_hidden': False
        },
        {
            'title': 'NoSQL Databases',
            'category': 'Database',
            'level': 'intermediate',
            'description': 'Introduction to NoSQL databases including MongoDB, Redis, and Cassandra. Learn when and how to use each type.',
            'is_hidden': False
        },
        {
            'title': 'Data Analytics with Python',
            'category': 'Data Science',
            'level': 'intermediate',
            'description': 'Learn data analysis using Python libraries like Pandas, NumPy, and Matplotlib. Clean, analyze, and visualize data.',
            'is_hidden': False
        },
        {
            'title': 'Docker and Containerization',
            'category': 'DevOps',
            'level': 'intermediate',
            'description': 'Learn Docker for containerization. Build, deploy, and manage containerized applications with Docker and Docker Compose.',
            'is_hidden': False
        },
        {
            'title': 'Kubernetes Orchestration',
            'category': 'DevOps',
            'level': 'advanced',
            'description': 'Master Kubernetes for container orchestration. Learn pods, services, deployments, and scaling applications.',
            'is_hidden': False
        },
        {
            'title': 'AWS Cloud Fundamentals',
            'category': 'Cloud',
            'level': 'intermediate',
            'description': 'Introduction to Amazon Web Services. Learn EC2, S3, RDS, and other core AWS services for cloud deployment.',
            'is_hidden': False
        },
        {
            'title': 'CI/CD Pipelines',
            'category': 'DevOps',
            'level': 'intermediate',
            'description': 'Build continuous integration and deployment pipelines. Learn Jenkins, GitHub Actions, and automated testing.',
            'is_hidden': False
        },
        {
            'title': 'Hidden Admin Course',
            'category': 'Administration',
            'level': 'advanced',
            'description': 'This course is hidden from regular users. Contains sensitive information about system administration and security configurations.',
            'is_hidden': True
        },
        {
            'title': 'System Administration Secrets',
            'category': 'Administration',
            'level': 'advanced',
            'description': 'Advanced system administration techniques and security configurations. Restricted to administrators only.',
            'is_hidden': True
        },
        {
            'title': 'Project Management Fundamentals',
            'category': 'Business',
            'level': 'beginner',
            'description': 'Learn project management principles, methodologies, and tools. Master planning, execution, and team coordination.',
            'is_hidden': False
        },
        {
            'title': 'Agile and Scrum',
            'category': 'Business',
            'level': 'intermediate',
            'description': 'Understand Agile methodologies and Scrum framework. Learn sprints, user stories, and agile team practices.',
            'is_hidden': False
        },
        {
            'title': 'Technical Writing',
            'category': 'Business',
            'level': 'beginner',
            'description': 'Learn to write clear, concise technical documentation. Master API documentation, user guides, and technical reports.',
            'is_hidden': False
        },
    ]
    
    created_count = 0
    for course_data in courses_data:
        assigned_profile = None
        if course_data.get('is_hidden') and admin_profile:
            assigned_profile = admin_profile
        elif profile_cycle:
            assigned_profile = next(profile_cycle)
        elif admin_profile:
            assigned_profile = admin_profile

        course_defaults = dict(course_data)
        if assigned_profile:
            course_defaults['userprofile'] = assigned_profile

        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults=course_defaults
        )
        if created:
            created_count += 1
            print(f"Created course: {course.title}")
        else:
            for key, value in course_data.items():
                setattr(course, key, value)
            if assigned_profile:
                course.userprofile = assigned_profile
            course.save()
    
    print(f"\nTotal courses: {Course.objects.count()} (created {created_count} new)")

def create_enrollments(users):
    courses = Course.objects.filter(is_hidden=False)[:3]
    for user in users[:2]:
        for course in courses:
            enrollment, created = Enrollment.objects.get_or_create(
                user=user,
                course=course
            )
            if created:
                print(f"Enrolled {user.username} in {course.title}")

def main():
    print("=" * 60)
    print("Initializing LMS Portal Data")
    print("=" * 60)
    admin_user = create_superuser()
    admin_profiles = create_user_profiles([admin_user])
    admin_profile = admin_profiles[0] if admin_profiles else None
    print("\n" + "-" * 60)
    print("Creating test users...")
    test_users = create_test_users()
    test_profiles = create_user_profiles(test_users)
    print("\n" + "-" * 60)
    print("Creating courses...")
    create_courses(test_profiles, admin_profile)
    print("\n" + "-" * 60)
    print("Creating enrollments...")
    create_enrollments(test_users)
    
    print("\n" + "=" * 60)
    print("Data initialization completed!")
    print("=" * 60)
    print("\nCredentials file:")
    print("  /root/lab_credentials.txt")

if __name__ == '__main__':
    main()
