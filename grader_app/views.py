import datetime
import email.message
import email.message
import json
import smtplib
import re
import pytz
from django import forms
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from requests_oauthlib import OAuth2Session
from .forms import EssayForm, LoginForm, InfoForm, ChangeForm, TeacherForm, AssignmentForm, \
    CommentForm, RegisterForm, SetupForm
from .models import Essay, Assignment, Comment
from .models import User
from .tasks import grade_all
from html import unescape
from unicodedata import normalize
from celery.result import ResultBase


# Create your views here.

# noinspection PyUnresolvedReferences
def login(request):
    admins = {"2023avasanth", "2023pbhandar", "2023kbhargav"}

    if request.user is not None and request.user.is_authenticated:
        return redirect("home")

    context = {
        'url': 'login'
    }
    client_id = "FeZBHle5SNytiEwAh333mPmoEmfFDQSF1Jigy2bW"
    client_secret = "saNPOvrrCGhNK1TywLjTsKo3M5uFzfQEgUtTpvvZsNIQPB75eeWYqhBxYMZJb0lKG5LZRZx" \
                    "1ZVN7ZUEiUUUqPeE8GMH0ZwdhbG4yNKKYmcCDu0UXV2gopeUB3B4cAIzw"
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            mail_id = form.cleaned_data["email"]
            if User.objects.filter(email=mail_id).exists():
                user = auth.authenticate(email=mail_id, password=form.cleaned_data["password"])
                if user is not None:
                    auth.login(request, user)
                    return redirect("http://localhost:8000/home")
            else:
                form = LoginForm()
                context['form'] = form

            context['error'] = "Username or Password is incorrect"
        else:
            form = LoginForm()
            context['form'] = form

    elif request.method == "GET" or request.user is None:
        form = LoginForm()
        context['form'] = form
        oauth = OAuth2Session(client_id,
                              redirect_uri="http://localhost:8000/login",
                              scope=["read"])
        authorization_url, state = oauth.authorization_url("https://ion.tjhsst.edu/oauth/authorize/")
        context['url'] = authorization_url
        if "code" in request.GET:
            CODE = request.GET.get("code")

            oauth.fetch_token("https://ion.tjhsst.edu/oauth/token/",
                              code=CODE,
                              client_secret=client_secret)

            try:
                raw_profile = oauth.get("https://ion.tjhsst.edu/api/profile")
                profile = json.loads(raw_profile.content.decode())
                mail_id = profile["tj_email"]
                if User.objects.filter(email=mail_id).exists():
                    user = auth.authenticate(email=mail_id,
                                             password=profile.get("ion_username") + profile.get("user_type"))
                    if user is not None:
                        auth.login(request, user)
                        user = request.user
                        user.logged_with_ion = True
                        user.save()
                        return redirect("http://localhost:8000/home")

                else:
                    if profile.get("ion_username") in admins or profile.get("is_eighth_admin"):
                        new_user = User.objects.create_superuser(email=mail_id,
                                                                 password=profile.get("ion_username") + profile.get(
                                                                     "user_type"))
                    elif profile.get("is_teacher"):
                        new_user = User.objects.create_teacheruser(email=mail_id,
                                                                   password=profile.get("ion_username") + profile.get(
                                                                       "user_type"))
                    else:
                        new_user = User.objects.create_studentuser(email=mail_id,
                                                                   password=profile.get("ion_username") + profile.get(
                                                                       "user_type"))
                    new_user.logged_with_ion = True
                    new_user.first_name = profile.get("first_name")
                    new_user.middle_name = profile.get("middle_name")
                    new_user.last_name = profile.get("last_name")
                    new_user.year_in_school = profile.get("grade").get("name").upper()[:3]
                    new_user.save()
                    user = auth.authenticate(email=mail_id,
                                             password=profile.get("ion_username") + profile.get("user_type"))
                    auth.login(request, user)
                    return redirect("http://localhost:8000/home")

            except Exception:
                args = {"client_id": client_id, "client_secret": client_secret}
                oauth.refresh_token("https://ion.tjhsst.edu/oauth/token/", **args)
    return render(request, "login.html", context)


def logout(request):
    auth.logout(request)
    return redirect("home")


def create(request):
    if request.user.is_authenticated:
        return redirect("home")
    context = {"method": request.method}
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            error = False
            mail = password = ""
            try:
                mail = form.cleaned_data.get('email')
                qs = User.objects.filter(email=mail)
                if qs.exists():
                    raise forms.ValidationError("email is taken")
            except forms.ValidationError:
                error = True

            try:
                password = form.clean_password2()
                if len(password) < 8:
                    raise ValueError
            except forms.ValidationError:
                error = True
            except ValueError:
                error = True

            specs = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
            numbers = "0123456789"
            special = False
            for char in specs:
                special = special or password.__contains__(char)
            number = False
            for char in numbers:
                number = number or password.__contains__(char)
            upper = False
            lower = False
            for char in password:
                if char.lower() == char:
                    lower = True
                else:
                    upper = True
            upandlow = lower and upper

            if not error and upandlow and number and special:
                new_user = User.objects.create_studentuser(email=mail, password=password)
                new_user.save()
                user = auth.authenticate(email=mail, password=password)
                auth.login(request, user)
                return redirect("http://localhost:8000/setup")
            else:
                form = RegisterForm()
                context['form'] = form
        else:
            form = RegisterForm()
            context['form'] = form

    else:
        form = RegisterForm()
        context['form'] = form
    return render(request, "create.html", context)


def setup(request):
    context = {
        "method": request.method,
        "form": SetupForm()
    }
    if context['method'] == "POST":
        form = SetupForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data.get('first_name')
            user.middle_name = form.cleaned_data.get('middle_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.year_in_school = form.cleaned_data.get('year_in_school')
            user.save()
            return redirect("home")
    return render(request, "setup.html", context)


def index(request):
    if request.user.is_authenticated:
        essays = []
        query = ""

        if request.GET:
            query = request.GET.get('q', 'Search for an essay')

        if query != "":
            profile = request.user
            queryset = []
            queries = query.split(" ")

            for q in queries:
                essays = Essay.objects.filter(author=profile).filter(
                    Q(title__icontains=q) |
                    Q(body__icontains=q)
                ).order_by('-created_on').distinct()

                for essay in essays:
                    queryset.append(essay)

            essays = list(set(queryset))

        if request.user.teacher and not request.user.admin:
            return redirect("teacher")

        if not essays:
            essays = Essay.objects.all().filter(author=request.user).order_by('-created_on')

        context = {
            "essays": essays,
            "query": str(query),
            "search": query != ""
        }

        return render(request, "index.html", context)

    else:
        return render(request, "index.html")

@login_required(login_url="login")
def submit(request):
    form = EssayForm(request.POST or None, **{'user': request.user})
    if request.method == 'POST':

        if form.is_valid():
            data = format_body(form.data["body"])
            essay = Essay(
                title=form.cleaned_data["title"],
                body=form.data["body"],
                author=request.user,
                assignment=form.cleaned_data["assignment"],
                teacher=User.objects.get(email=form.cleaned_data["teachers"]),
                citation_type=form.cleaned_data["citation_type"],
                marked_body=data,
                raw_body=data,
            )
            essay.save()
            # message = "Your student %s has just submitted an essay for the assignment %s. " \
            #           "\n\nYou also currently have %s submissions for that assignment." \
            #           "\n\n-------------------------------------------------\n\n%s\n\n%s" % (
            #               request.user, new_assignment.assignment_name,
            #               Essay.objects.filter(assignment=new_assignment).count(),
            #               essay.title,
            #               essay.body[:400] + "...")

            # send_email(message=message, subject="New submission for assignment %s." % new_assignment.assignment_name,
            #            emails=[form.cleaned_data["teachers"]])
            return redirect("home")
    context = {
        'form': form,
    }
    return render(request, "submit.html", context)


def format_body(body):
    formatted_body = unescape(body)
    formatted_body = normalize("NFKC", formatted_body)
    tags = re.findall("<[^<]+?>", formatted_body)
    for i in tags:
        if "<p" in i:
            formatted_body = formatted_body.replace(i, "\n")
        elif i != "<em>" and i != "</em>":
            formatted_body = formatted_body.replace(i, "")

    formatted_body = formatted_body.replace("    ", "")
    formatted_body = formatted_body.replace("<em>", "<i>")
    formatted_body = formatted_body.replace("</em>", "</i>")
    return formatted_body


def load_assignments(request):
    user_teacher = request.GET.get('teacher')
    if "-SELECT-" != user_teacher:
        assigns = User.objects.get(email=user_teacher).assignments.all()
    else:
        assigns = Assignment.objects.none()
    return render(request, 'submit_options.html', {'assignments': assigns})


def load_essay(request):
    essay_pk = request.GET.get('pk')
    essay = Essay.objects.get(pk=essay_pk)
    comments = Comment.objects.filter(essay=essay)
    form = CommentForm(None)
    data = {
        'essay': essay,
        'comments': comments,
        'form': form
    }
    return render(request, 'load_essay.html', data)


@login_required(login_url="login")
def detail(request, pk):
    essay = Essay.objects.get(pk=pk)

    if request.method == "POST":

        form = CommentForm(request.POST or None)
        if form.is_valid():
            c = Comment(
                author=request.user,
                body=form.cleaned_data.get("Comment"),
                essay=essay
            )
            c.save()

    form = CommentForm(None)
    comments = Comment.objects.filter(essay=essay)
    context = {
        'essay': essay,
        'comments': comments,
        'form': form
    }

    return render(request, "detail.html", context)


@login_required(login_url="login")
def grade(request, pk):  # max 7973 characters/request, <100 requests/day
    if not request.user.teacher:
        return redirect("home")

    essays = Essay.objects.all().filter(assignment=Assignment.objects.get(pk=pk))
    essay_list = []

    for i in essays:
        x = [i.author.first_name + " " + i.author.last_name, i.title, i.raw_body]  # (author, title, essay)
        citation_type = i.citation_type

        if citation_type == "APA":
            citation_heading = "References"
        else:
            citation_heading = "Works Cited"

        if citation_heading in x[-1]:
            x[-1] = citation_heading.join(x[-1].split(citation_heading)[:-1]).replace("\r", "").replace("\n", "")
            # get rid of the citation section in the essay

        x = tuple(x)

        essay_list.append(x)

    essay_tuples = []

    for essay in essays:
        if not essay.marked and essay.citation_type != "None":
            author = essay.author.first_name + " " + essay.author.last_name
            x = essay.id, essay.raw_body, essay.citation_type, author, essay.title
            essay_tuples.append(x)

    ret = grade_all.delay(essay_tuples, essay_list)

    results = ret.get()

    for result in results:
        # print("Original", result[1])
        essay = Essay.objects.get(id=result[0])
        essay.marked_body = result[1]
        essay.marked = True
        essay.save()

    essays = Essay.objects.all().filter(assignment=Assignment.objects.get(pk=pk))

    context = {
        'essays': essays
    }

    return render(request, "grade.html", context)


def reformat(body):
    temp = body.split("\r\n")
    tempText = "<p>"

    for paragraph in temp:
        tempText += paragraph + "</p><p>"

    # print("Added para statements", tempText)

    temp = tempText.split("\t")
    tempText = "&emsp;"

    for tab in temp:
        tempText += tab + "&emsp;"

    # print("Added tab statements", tempText)

    return tempText + "</p>"


@login_required(login_url="login")
def teacher(request):
    context = {}
    user = request.user

    if not user.teacher:
        redirect("home")

    context['assignments'] = Assignment.objects.all()
    return render(request, "teacher.html", context)


def teacher_graded(request, pk):
    context = {}
    user = request.user

    if not user.teacher:
        redirect("home")

    if Assignment.objects.filter(pk=pk).exists():
        all_assignments = Assignment.objects.get(pk=pk)
        graded = Essay.objects.filter(assignment=all_assignments, graded=True)
    else:
        all_assignments = "None"
        graded = []
        context['error'] = "That Assignment Request Does Not Exist"
    context['assignment'] = all_assignments
    context['graded'] = graded
    return render(request, "teacher_graded.html", context)


def teacher_not_graded(request, pk):
    context = {}
    user = request.user

    if not user.teacher:
        redirect("home")

    if Assignment.objects.filter(pk=pk).exists():
        all_assignments = Assignment.objects.get(pk=pk)
        not_graded = Essay.objects.filter(assignment=all_assignments, graded=False)
    else:
        all_assignments = "None"
        not_graded = []
        context['error'] = "That Assignment Request Does Not Exist"
    context['assignment'] = all_assignments
    context['not_graded'] = not_graded
    return render(request, "teacher_not_graded.html", context)


@login_required(login_url="login")
def settings_changeInfo(request):
    profile = request.user

    context = {}
    if request.method == 'POST':
        form = InfoForm(request.POST)

        if form.is_valid():
            profile.email = form.cleaned_data.get('email')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.middle_name = form.cleaned_data.get('middle_name')
            profile.last_name = form.cleaned_data.get('last_name')
        profile.save()

    form = InfoForm(
        initial={'email': profile.email, 'first_name': profile.first_name, 'middle_name': profile.middle_name,
                 'last_name': profile.last_name})

    if profile.logged_with_ion:
        form.disable()
        context['error'] = "Cannot change info due to Ion login"
    context['form'] = form

    return render(request, "settings_info.html", context)


@login_required(login_url="login")
def settings_changePassword(request):
    profile = request.user

    context = {}

    if request.method == 'POST':
        form = InfoForm(request.POST)

        if form.is_valid():
            password1 = form.cleaned_data.get('password_1')
            password2 = form.cleaned_data.get('password_2')
            if password1 != password2:
                context['error'] = "Passwords do not match"
            else:
                profile.set_password()

    form = ChangeForm()

    if profile.logged_with_ion:
        form.disable()
        context['error'] = 'Cannot change info due to Ion login'
    context['form'] = form

    return render(request, "settings_password.html", context)


@login_required(login_url="login")
def settings_changeTeachers(request):
    profile = request.user
    context = {}

    names = [
        "period_1_teacher",
        "period_2_teacher",
        "period_3_teacher",
        "period_4_teacher",
        "period_5_teacher",
        "period_6_teacher",
        "period_7_teacher",
    ]

    initial = {}

    user_teacher = profile.get_teachers()

    for name in names:
        initial[name] = user_teacher.get(name)

    if request.method == 'POST':
        form = TeacherForm(request.POST)

        if form.is_valid():
            teachers = {}
            error = False
            for name in names:
                teachers[name] = form.cleaned_data.get(name)
                if teachers[name] != "":
                    if not User.objects.filter(email=teachers[name]).exists():
                        error = True
                        context['error'] = "The email %s is either incorrect or doesn't belong to a user. Your " \
                                           "information has not been saved." % teachers[name]
                        break
                    if list(teachers.values()).count(teachers[name]) > 1:
                        error = True
                        context['error'] = "You have repeated the email ' %s ' twice. Please remove one instance and " \
                                           "try again." % teachers[name]
            if not error:
                profile.set_teachers(teachers)
                profile.save()
                message = "The student - %s - has added you in their teachers list." \
                          "\n\nIf this is a mistake please contact them at \"%s\"" % (
                              request.user.get_full_name(), request.user.email)
                emails = list()
                for user_teacher in teachers.values():
                    if user_teacher != "" and user_teacher not in initial.values():
                        emails.append(user_teacher)

                send_email(message, "New Student Alert", emails)

                context['saved'] = True
        else:
            context['error'] = "Invalid Email(s)"

    form = TeacherForm(initial)

    context['form'] = form

    user_teacher = profile.get_teachers()

    for name in names:
        initial[name] = user_teacher.get(name)

    return render(request, "settings_teacher.html", context)


@login_required(login_url="login")
def assignment(request):
    if request.user.teacher:
        context = {"form": AssignmentForm()}
        if request.method == "POST":
            user = request.user
            form = AssignmentForm(request.POST)

            if form.is_valid():
                a = Assignment(
                    assignment_description=form.cleaned_data.get("assignment_description"),
                    assignment_name=form.cleaned_data.get("assignment_name"),
                    due_date=request.POST.get('due_date')
                )
                a.save()
                user.assignments.add(a)
                user.save()

                students = list()
                for student in User.objects.all().filter(student=True):
                    for teacher_user in student.get_teachers().values():
                        if teacher_user != "":
                            t = User.objects.get(email=teacher_user)
                            if t.email == user.email:
                                students.append(student.email)

                message = """Your teacher %s has just posted a new assignment - %s.\n\nAssignment description: %s""" % (
                    user.get_full_name(), a.assignment_name, a.assignment_description)
                send_email(message, "New Assignment Alert", students)
                return redirect("home")

        return render(request, "assignment.html", context)
    else:
        return redirect("home")


def send_email(message, subject, emails):
    m = email.message.Message()
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login('essay.grader.app@gmail.com', 'grader_app@7876')  # login with mail_id and password
    for receiver_address in emails:
        m['From'] = "essay.grader.app@gmail.com"
        m['To'] = str(receiver_address)
        m['Subject'] = subject
        m.set_payload(message)
        session.sendmail('essay.grader.app@gmail.com', receiver_address, m.as_string())
    session.quit()


def validate_due_date(request):
    check_assignment = Assignment.objects.get(pk=request.GET.get('pk'))
    split = check_assignment.due_date.split(' ')
    date = split[0].split('/')
    time = split[1].split(':')
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])
    hour = int(time[0])
    minute = int(time[1])
    seconds = int(00)
    if split[2] == "PM":
        hour += 12
    due_date_time = datetime.datetime(year, month, day, hour, minute, seconds).replace(
        tzinfo=pytz.timezone('US/Eastern'))
    today = datetime.datetime.now().replace(tzinfo=pytz.timezone('US/Eastern'))
    return JsonResponse({'expired': (today > due_date_time)})


def grade_essay(request, pk):
    essay = Essay.objects.get(pk=pk)
    if request.GET.get('denominator') != '' and request.GET.get('denominator') != 0 and request.GET.get(
            'numerator') != '':
        essay.grade_numerator = int(request.GET.get('numerator'))
        essay.grade_denominator = int(request.GET.get('denominator'))
        essay.graded = True
        essay.save()
    return JsonResponse({})


def comment(request):
    essay = Essay.objects.get(pk=request.GET.get('pk'))
    comm = Comment(essay=essay, body=request.GET.get('body'), author=User.objects.get(email=request.GET.get("email")))
    comm.save()
    return JsonResponse({})


def dark(request):
    u = User.objects.get(email=request.GET.get("email"))
    if request.GET.get("dark") == "true":
        u.dark_mode = True
    else:
        u.dark_mode = False
    u.save()
    return JsonResponse({})


def validate_user_email(request):
    valid = not User.objects.all().filter(email=request.GET.get("email")).exists()
    if valid:
        valid = not request.GET.get("email") == ""
        if valid:
            valid = request.GET.get("email").__contains__("@")
            if valid:
                valid = request.GET.get("email").__contains__(".")


    return JsonResponse({"valid": valid})


def validate_user_password(request):
    password1 = request.GET.get('password1')
    password2 = request.GET.get('password2')
    specs = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
    numbers = "0123456789"
    match = password1 == password2
    length = len(password1) >= 8
    special = False
    for char in specs:
        special = special or password1.__contains__(char)
    number = False
    for char in numbers:
        number = number or password1.__contains__(char)
    upper = False
    lower = False
    for char in password1:
        if char.lower() == char:
            lower = True
        else:
            upper = True
    upandlow = lower and upper
    data = {
        "match" : match,
        "length" : length,
        "special" : special,
        "number" : number,
        "upandlow" : upandlow
    }
    return JsonResponse(data)
