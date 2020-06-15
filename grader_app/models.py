import json

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db import models


# Create your models here.
class Comment(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    essay = models.ForeignKey('Essay', on_delete=models.CASCADE)


class Assignment(models.Model):
    assignment_name = models.CharField(max_length=150, blank=False)
    assignment_description = models.TextField()
    due_date = models.CharField(max_length=19)

    def __str__(self):
        return self.assignment_name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_studentuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.student = True
        user.save(using=self._db)
        return user

    def create_teacheruser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.teacher = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.teacher = True
        user.admin = True
        user.student = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50)
    logged_with_ion = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)

    teachers = models.TextField(default=json.dumps({
        "period_1_teacher": "",
        "period_2_teacher": "",
        "period_3_teacher": "",
        "period_4_teacher": "",
        "period_5_teacher": "",
        "period_6_teacher": "",
        "period_7_teacher": "",
    }))

    def set_teachers(self, teacher):
        self.teachers = json.dumps(teacher)
        self.save()

    def get_teachers(self):
        return json.loads(self.teachers)

    assignments = models.ManyToManyField(Assignment)

    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    GRADUATE = 'GR'

    YEAR_IN_SCHOOL_CHOICES = [
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (GRADUATE, 'Graduate'),
    ]
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )
    student = models.BooleanField(default=False)
    teacher = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def username(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_identification(self):
        return self.email

    def get_email(self):
        return self.email

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def get_grade(self):
        return self.year_in_school

    def __str__(self):
        return self.get_full_name()

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
        return True

    @property
    def is_student(self):
        return self.student

    @property
    def is_staff(self):
        return self.teacher

    @property
    def is_admin(self):
        return self.admin

    objects = UserManager()


class Essay(models.Model):
    dropdown = (("APA", "APA"), ("MLA", "MLA"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="teacher", null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=500)
    body = models.TextField()
    raw_body = models.TextField(default="")
    created_on = models.DateTimeField(auto_now_add=True)
    citation_type = models.CharField(max_length=150, choices=dropdown, default="None")
    marked_body = models.TextField(default="")
    graded = models.BooleanField(default=False)
    marked = models.BooleanField(default=False)
    grade_numerator = models.IntegerField(default=0)
    grade_denominator = models.IntegerField(default=0)
